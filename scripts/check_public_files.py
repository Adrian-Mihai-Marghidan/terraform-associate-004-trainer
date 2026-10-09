#!/usr/bin/env python3
"""Check publishable files for known private artifacts and personal home paths.

By default inspect the Git index, not ignored local files. Use --filesystem on
a Git-free export. This focused check is not a general-purpose secret scanner.
"""
import argparse
import fnmatch
import re
import subprocess
from pathlib import Path


PRIVATE_DIRECTORIES = {"private", ".tools", ".terraform", ".simulator", ".aws"}
PRIVATE_NAMES = {"plan.out", ".terraformrc", "terraform.rc", "credentials.tfrc.json", ".DS_Store"}
PRIVATE_PATTERNS = (
    "*.tfstate", "*.tfstate.*", "*.tfplan", "*.plan", "*.log", "*.log.*",
    "*.simulator.json", "*.simulator.json.lock", "*.db", "*.sqlite", "*.sqlite3",
    "*.pem", "*.key", "override.tf", "override.tf.json", "*_override.tf", "*_override.tf.json",
)
# Build the prefixes separately so this check does not flag its own source.
PERSONAL_HOME = re.compile(
    r"(?:/" + r"Users/|/" + r"home/)[A-Za-z0-9_.-]+(?:/|(?=[\s\"'`])|$)"
    r"|[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+(?:\\|(?=[\s\"'`])|$)"
)


def private_path(path):
    """Return a reason for a forbidden public path, or None."""
    relative = Path(path)
    if any(part in PRIVATE_DIRECTORIES for part in relative.parts):
        return "private or generated directory"
    name = relative.name
    if name in PRIVATE_NAMES or any(fnmatch.fnmatchcase(name, pattern) for pattern in PRIVATE_PATTERNS):
        return "private or generated file"
    if (name == ".env" or name.startswith(".env.")) and name != ".env.example":
        return "environment credential file"
    if (name.endswith(".tfvars") or name.endswith(".tfvars.json")) and not (
        name.endswith(".example.tfvars") or name.endswith(".example.tfvars.json")
    ):
        return "non-example Terraform variable file"
    return None


def git_index_files(root):
    """Read indexed blobs, including files ignored or modified in the worktree."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, filename = entry.split(b"\t", 1)
        mode, object_id, stage = metadata.decode("ascii").split()
        path = filename.decode("utf-8", errors="surrogateescape")
        if stage != "0":
            raise ValueError("Resolve the Git index conflict before checking public files: " + path)
        if mode == "160000":
            raise ValueError("Review submodule content separately before publication: " + path)
        blob = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", object_id],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        yield path, blob.stdout


def filesystem_files(root):
    """Read an export; do not silently hide private artifacts in that export."""
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts:
            continue
        if path.is_symlink():
            # Check the published link target without traversing external files.
            yield relative.as_posix(), str(path.readlink()).encode()
        elif path.is_file():
            yield relative.as_posix(), path.read_bytes()


def check(root, mode="index"):
    root = Path(root).resolve()
    entries = git_index_files(root) if mode == "index" else filesystem_files(root)
    issues = []
    count = 0
    for relative, content in entries:
        count += 1
        reason = private_path(relative)
        if reason:
            issues.append(f"{relative}: {reason} must remain outside public Git history")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if PERSONAL_HOME.search(line):
                issues.append(f"{relative}:{number}: personal absolute home path; use a relative path or placeholder")
    if not count:
        issues.append("No public files were checked; stage files or select --filesystem for an export")
    return issues, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--filesystem", action="store_true", help="check all files in a Git-free export")
    args = parser.parse_args()
    try:
        issues, count = check(args.root, "filesystem" if args.filesystem else "index")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Public-file check could not run: {error}\n")
    if issues:
        parser.exit(1, "Public-file check failed:\n" + "\n".join(issues) + "\n")
    print(f"Public-file checks passed: {count} files; known private artifacts and personal home paths excluded.")
    print("This focused check does not prove that every credential or personal detail is absent.")


if __name__ == "__main__":
    main()
