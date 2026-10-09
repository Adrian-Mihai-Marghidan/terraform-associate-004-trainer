#!/usr/bin/env python3
"""Build and connect the sibling simulator without changing global CLI settings."""
import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "terraform.local/learning/azuresim"
VERSION = "0.1.1"


def atomic_write(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        pending = Path(temporary.name)
        temporary.write(content)
    try:
        pending.chmod(mode)
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)


def install_built_tools(built, simulator, tools, version):
    """Preflight all artifacts before changing the active setup; versions are immutable."""
    target = version["platform"]
    mirror = tools / "provider-mirror"
    binary = mirror / SOURCE / VERSION / target / f"terraform-provider-azuresim_v{VERSION}"
    provider_bytes = (built / "terraform-provider-azuresim").read_bytes()
    simctl_bytes = (built / "simctl").read_bytes()
    if binary.exists() and binary.read_bytes() != provider_bytes:
        raise ValueError(f"Existing {VERSION} package checksum differs; preserved installed tools. "
                         "Verify the source/toolchain and release a new version instead of overwriting a locked package.")
    config = tools / "simulator.tfrc"
    config_text = ("disable_checkpoint = true\nprovider_installation {\n  filesystem_mirror {\n"
                   f"    path = {json.dumps(str(mirror))}\n"
                   f"    include = [{json.dumps(SOURCE)}]\n  }}\n}}\n")
    private = ROOT / "private"
    record = {
        "provider_source": SOURCE, "provider_version": VERSION,
        "simulator_root": str(simulator), "platform": target,
        "provider_binary": str(binary), "provider_sha256": hashlib.sha256(provider_bytes).hexdigest(),
        "terraform_binary": str(tools / "terraform/terraform"), "terraform_version": version["terraform_version"],
        "simctl_binary": str(tools / "bin/simctl"), "simctl_sha256": hashlib.sha256(simctl_bytes).hexdigest(),
        "cli_config": str(config),
    }
    record_bytes = (json.dumps(record, indent=2) + "\n").encode()
    active_record = private / "SIMULATOR_SETUP.json"
    if active_record.exists():
        previous = json.loads(active_record.read_text())
        if not isinstance(previous, dict):
            raise ValueError("Existing simulator setup record is invalid; preserve it and investigate.")
        identity = ("provider_source", "provider_version", "platform")
        if all(previous.get(key) == record[key] for key in identity) and previous.get("provider_sha256") != record["provider_sha256"]:
            raise ValueError(f"Existing setup records a different {VERSION} checksum; preserved installed tools. "
                             "Restore the verified package or release a new version.")
    if active_record.exists() and active_record.read_bytes() != record_bytes:
        stamp = datetime.now(ZoneInfo("Europe/Bucharest")).strftime("%Y%m%dT%H%M%S%f")
        backup = private / "development/setup-history" / stamp
        for existing in (active_record, private / "simulator-env.sh", config,
                         tools / "bin/simctl", tools / "bin/terraform-provider-azuresim"):
            if existing.is_file():
                atomic_write(backup / existing.name, existing.read_bytes(), existing.stat().st_mode & 0o777)
    if not binary.exists():
        atomic_write(binary, provider_bytes, 0o755)
    atomic_write(tools / "bin/terraform-provider-azuresim", provider_bytes, 0o755)
    atomic_write(tools / "bin/simctl", simctl_bytes, 0o755)
    atomic_write(config, config_text.encode())
    atomic_write(active_record, record_bytes)
    atomic_write(private / "simulator-env.sh", (
        "# Source in this terminal; global tools and settings are unchanged.\n"
        f"export PATH={shlex.quote(str(tools / 'terraform'))}:{shlex.quote(str(tools / 'bin'))}:\"$PATH\"\n"
        f"export TF_CLI_CONFIG_FILE={shlex.quote(str(config))}\n"
        "export CHECKPOINT_DISABLE=1\n"
    ).encode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulator-root", type=Path, default=ROOT.parent / "terraform-azure-simulator")
    args = parser.parse_args()
    simulator = args.simulator_root.resolve()
    if not (simulator / "scripts/build.py").is_file():
        parser.error(f"Simulator implementation missing at {simulator}; documentation alone is not an implementation.")
    tools = ROOT / ".tools"
    go = tools / "go/bin/go"
    terraform = tools / "terraform/terraform"
    if not go.is_file() or not terraform.is_file():
        parser.error("Run python3 scripts/install_local_tools.py first. Global Terraform is not changed.")
    env = os.environ.copy()
    env["CHECKPOINT_DISABLE"] = "1"
    version = json.loads(subprocess.check_output([str(terraform), "version", "-json"], env=env))
    if not version["terraform_version"].startswith("1.12."):
        parser.error("The isolated CLI must be Terraform 1.12.x for this exam target.")
    target = version["platform"]
    if not target.startswith(("darwin_", "linux_")):
        parser.error("Simulator supports macOS and Linux/WSL2.")
    with tempfile.TemporaryDirectory(prefix="simulator-build-", dir=tools) as directory:
        built = Path(directory)
        subprocess.run([sys.executable, str(simulator / "scripts/build.py"), "--go", str(go),
                        "--output", str(built), "--cache", str(tools), "--test"], check=True)
        install_built_tools(built, simulator, tools, version)
    print("Local mirror configured with only the simulator provider; no direct registry fallback.")
    print("Next: source private/simulator-env.sh")


if __name__ == "__main__":
    main()
