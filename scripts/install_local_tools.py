#!/usr/bin/env python3
"""Install checksum-verified, isolated tools; never change global Terraform."""
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".tools"
DOWNLOADS = TOOLS / "downloads"
TERRAFORM_VERSION = "1.12.2"
GO_VERSION = "go1.27.2"


def atomic_copy(source, target):
    """Publish a complete file without leaving partial cache entries on failure."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    pending = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False) as output:
            pending = Path(output.name)
            shutil.copyfileobj(source, output)
        os.replace(pending, target)
    finally:
        if pending is not None and pending.exists():
            pending.unlink()


def download(url, target):
    target = Path(target)
    if not target.exists():
        print(f"Downloading {url}", flush=True)
        with urllib.request.urlopen(url, timeout=120) as response:
            atomic_copy(response, target)
    return target


def checksum(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path, expected):
    if checksum(path) != expected:
        raise SystemExit(f"Checksum mismatch for {path}; preserved the file for investigation.")


def archive_with_legacy_cache(url, filename, legacy_filename, expected):
    target = DOWNLOADS / filename
    legacy = DOWNLOADS / legacy_filename
    if not target.exists() and legacy.is_file() and checksum(legacy) == expected:
        with legacy.open("rb") as source:
            atomic_copy(source, target)
        print(f"Reused verified cached archive {legacy.name} as {filename}", flush=True)
    archive = download(url, target)
    verify(archive, expected)
    return archive


def tool_output(binary, *arguments, env=None):
    try:
        result = subprocess.run([str(binary), *arguments], env=env, text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Cannot verify existing tool {binary}; preserved it. {error}") from error
    return result.stdout


def verify_terraform(binary, os_name, arch):
    env = os.environ.copy()
    env["CHECKPOINT_DISABLE"] = "1"
    try:
        actual = json.loads(tool_output(binary, "version", "-json", env=env))
    except (ValueError, TypeError) as error:
        raise SystemExit(f"Cannot read Terraform version from {binary}; preserved it.") from error
    expected = {"terraform_version": TERRAFORM_VERSION, "platform": f"{os_name}_{arch}"}
    if any(actual.get(key) != value for key, value in expected.items()):
        raise SystemExit(f"Terraform tool mismatch at {binary}: expected {expected}, got {actual}. "
                         "Preserved the existing installation; review it before replacement.")


def verify_go(binary, os_name, arch):
    env = os.environ.copy()
    # Avoid automatic toolchain downloads and inherited global Go installations.
    env["GOTOOLCHAIN"] = "local"
    env.pop("GOROOT", None)
    actual = tool_output(binary, "version", env=env).strip()
    expected = f"go version {GO_VERSION} {os_name}/{arch}"
    if actual != expected:
        raise SystemExit(f"Go tool mismatch at {binary}: expected {expected!r}, got {actual!r}. "
                         "Preserved the existing installation; review it before replacement.")
    try:
        host = json.loads(tool_output(binary, "env", "-json", "GOHOSTOS", "GOHOSTARCH", env=env))
    except (ValueError, TypeError) as error:
        raise SystemExit(f"Cannot read Go host platform from {binary}; preserved it.") from error
    if host.get("GOHOSTOS") != os_name or host.get("GOHOSTARCH") != arch:
        raise SystemExit(f"Go host mismatch at {binary}: expected {os_name}/{arch}, got {host}. "
                         "Preserved the existing installation; review it before replacement.")


def terraform_checksum(filename):
    manifest_name = f"terraform_{TERRAFORM_VERSION}_SHA256SUMS"
    target = DOWNLOADS / manifest_name
    legacy = DOWNLOADS / "terraform_SHA256SUMS"
    if not target.exists() and legacy.is_file():
        rows = [line.split() for line in legacy.read_text().splitlines()]
        if any(len(row) == 2 and row[1].lstrip("*") == filename for row in rows):
            with legacy.open("rb") as source:
                atomic_copy(source, target)
    base = f"https://releases.hashicorp.com/terraform/{TERRAFORM_VERSION}"
    manifest = download(f"{base}/{manifest_name}", target).read_text()
    rows = [line.split() for line in manifest.splitlines()]
    matches = [row[0] for row in rows if len(row) == 2 and row[1].lstrip("*") == filename]
    if len(matches) != 1 or len(matches[0]) != 64 or any(c not in "0123456789abcdef" for c in matches[0]):
        raise SystemExit(f"Invalid checksum entry for {filename} in {target}; preserved the manifest.")
    return matches[0]


def go_release(os_name, arch):
    metadata_path = DOWNLOADS / "go-releases.json"

    def select(metadata):
        return next((file for release in metadata for file in release["files"]
                     if file["version"] == GO_VERSION and file["os"] == os_name
                     and file["arch"] == arch and file["kind"] == "archive"), None)

    metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else []
    entry = select(metadata)
    if entry is None:
        with urllib.request.urlopen("https://go.dev/dl/?mode=json&include=all", timeout=120) as response:
            metadata = json.load(response)
        entry = select(metadata)
        if entry is None:
            raise SystemExit(f"Official Go metadata has no {GO_VERSION} archive for {os_name}/{arch}.")
        atomic_copy(io.BytesIO((json.dumps(metadata) + "\n").encode()), metadata_path)
    return entry


def install_terraform(os_name, arch):
    binary = TOOLS / "terraform/terraform"
    if binary.exists():
        verify_terraform(binary, os_name, arch)
        return
    filename = f"terraform_{TERRAFORM_VERSION}_{os_name}_{arch}.zip"
    base = f"https://releases.hashicorp.com/terraform/{TERRAFORM_VERSION}"
    archive = archive_with_legacy_cache(f"{base}/{filename}", filename, "terraform.zip", terraform_checksum(filename))
    binary.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TOOLS, prefix=".terraform-install-") as directory:
        staged = Path(directory) / "terraform"
        with zipfile.ZipFile(archive) as content, content.open("terraform") as source, staged.open("wb") as output:
            shutil.copyfileobj(source, output)
        staged.chmod(0o755)
        verify_terraform(staged, os_name, arch)
        os.replace(staged, binary)


def install_go(os_name, arch):
    directory = TOOLS / "go"
    if directory.exists():
        if not (directory / "bin/go").is_file():
            raise SystemExit(f"Incomplete Go installation at {directory}; preserved it for investigation.")
        verify_go(directory / "bin/go", os_name, arch)
        return
    entry = go_release(os_name, arch)
    archive = archive_with_legacy_cache(f"https://go.dev/dl/{entry['filename']}", entry["filename"],
                                        "go.tar.gz", entry["sha256"])
    with tempfile.TemporaryDirectory(dir=TOOLS, prefix=".go-install-") as stage:
        with tarfile.open(archive) as content:
            members = content.getmembers()
            for member in members:
                path = Path(member.name)
                if (path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "go"
                        or not (member.isfile() or member.isdir())):
                    raise SystemExit("Unsafe path or link in Go archive.")
            content.extractall(stage, members=members)
        staged = Path(stage) / "go"
        verify_go(staged / "bin/go", os_name, arch)
        if directory.exists():
            raise SystemExit(f"Go installation appeared at {directory}; preserved it instead of overwriting.")
        staged.rename(directory)


def main():
    if sys.version_info < (3, 9):
        raise SystemExit("Python 3.9 or newer is required for the mentor setup scripts.")
    os_name = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
    arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "amd64", "AMD64": "amd64"}.get(platform.machine())
    if not os_name or not arch:
        raise SystemExit("Supported hosts: macOS or Linux/WSL2, amd64 or arm64.")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    # Diagnose incompatible tools before making other installation changes.
    if (TOOLS / "go").exists():
        if not (TOOLS / "go/bin/go").is_file():
            raise SystemExit(f"Incomplete Go installation at {TOOLS / 'go'}; preserved it for investigation.")
        verify_go(TOOLS / "go/bin/go", os_name, arch)
    if (TOOLS / "terraform/terraform").exists():
        verify_terraform(TOOLS / "terraform/terraform", os_name, arch)
    install_terraform(os_name, arch)
    install_go(os_name, arch)
    print(f"Verified Terraform {TERRAFORM_VERSION} and {GO_VERSION} ({os_name}/{arch}) under {TOOLS}. Global tools unchanged.")


if __name__ == "__main__":
    main()
