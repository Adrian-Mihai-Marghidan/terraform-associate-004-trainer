#!/usr/bin/env python3
"""Verify a native simulator lock in a private copy; publish only with --write.

Maintenance setup, not a learner exercise. Source private/simulator-env.sh first.
Never runs plan/apply/import or copies learner state or infrastructure storage.
"""
import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import check_simulator

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "terraform.local/learning/azuresim"
LOCK_NAME = ".terraform.lock.hcl"


def lock_snapshot(path):
    """Detect edits, replacement, removal, and creation of the original lock."""
    if path.is_symlink():
        raise ValueError("Preserve and investigate the symlinked provider lock; it cannot be reconciled.")
    try:
        stat = path.stat()
    except FileNotFoundError:
        return None
    if not path.is_file():
        raise ValueError("The provider lock must be a regular file.")
    content = path.read_bytes()
    after = path.stat()
    identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
    if identity(stat) != identity(after):
        raise ValueError("Provider lock changed while reading; preserve it and retry without concurrent edits.")
    return {"content": content, "identity": identity(after), "mode": after.st_mode & 0o777}


def config_snapshot(lab):
    return {file.name: file.read_bytes() for file in sorted(lab.glob("*.tf"))}


def publish_lock(path, candidate, original, configuration, lab, setup_bytes, run_directory):
    """Serialize helper writers, preserve the prior lock, and replace atomically.

    Other editors must not change the lab concurrently. Snapshot checks detect
    changes during validation; the private advisory lock serializes this helper.
    """
    publication_lock = run_directory.parent / (hashlib.sha256(str(lab).encode()).hexdigest() + ".lock")
    with publication_lock.open("a+b") as lease:
        fcntl.flock(lease, fcntl.LOCK_EX)
        check_simulator.check(lab)
        if (ROOT / "private/SIMULATOR_SETUP.json").read_bytes() != setup_bytes:
            raise ValueError("Simulator setup changed during verification; no learner lock was written.")
        if config_snapshot(lab) != configuration:
            raise ValueError("Lab configuration changed during verification; no learner lock was written.")
        if lock_snapshot(path) != original:
            raise ValueError("Provider lock changed during verification; preserved the current learner lock.")
        if original is not None:
            backup = run_directory / "original.terraform.lock.hcl"
            backup.write_bytes(original["content"])
            backup.chmod(0o600)
        # Stage in the destination directory so publication is one atomic rename.
        with tempfile.NamedTemporaryFile(prefix=".simulator-lock-", dir=lab, delete=False) as staged:
            pending = Path(staged.name)
            staged.write(candidate)
        try:
            pending.chmod(original["mode"] if original is not None else 0o644)
            if lock_snapshot(path) != original or config_snapshot(lab) != configuration:
                raise ValueError("Lab or provider lock changed before publication; preserved the learner files.")
            if original is None:
                # Atomic create-if-absent: never overwrite a concurrently created lock.
                os.link(pending, path)
            else:
                pending.replace(path)
        finally:
            pending.unlink(missing_ok=True)


def reconcile(lab, write=False):
    lab = Path(lab).resolve()
    check_simulator.check(lab)
    setup_path = ROOT / "private/SIMULATOR_SETUP.json"
    setup_bytes = setup_path.read_bytes()
    setup = json.loads(setup_bytes)
    configuration = config_snapshot(lab)
    original_path = lab / LOCK_NAME
    original = lock_snapshot(original_path)
    base = ROOT / "private/development/lock-validation"
    base.mkdir(parents=True, exist_ok=True)
    run_directory = Path(tempfile.mkdtemp(prefix="native-", dir=base))
    copied = run_directory / "configuration"
    copied.mkdir()
    for name, content in configuration.items():
        (copied / name).write_bytes(content)
    if original is not None:
        (copied / LOCK_NAME).write_bytes(original["content"])
    env = os.environ.copy()
    env.update(TF_CLI_CONFIG_FILE=setup["cli_config"], CHECKPOINT_DISABLE="1", TF_IN_AUTOMATION="1")
    record = {"kind": "simulator-lock-maintenance", "learner_evidence": False,
              "started_at": datetime.now(timezone.utc).isoformat(), "lab": str(lab),
              "platform": setup["platform"], "provider_source": SOURCE,
              "write_requested": write, "checks": []}

    def execute(label, arguments):
        command = [setup["terraform_binary"], *arguments]
        result = subprocess.run(command, cwd=copied, env=env, text=True, capture_output=True)
        (run_directory / f"{label}.log").write_text(result.stdout + result.stderr)
        record["checks"].append({"label": label, "command": command, "exit_code": result.returncode})
        if result.returncode:
            raise RuntimeError(f"{label} failed with exit {result.returncode}; evidence: {run_directory}")

    try:
        execute("providers-lock", ["providers", "lock", f"-fs-mirror={ROOT / '.tools/provider-mirror'}",
                                   f"-platform={setup['platform']}", SOURCE])
        candidate = (copied / LOCK_NAME).read_bytes()
        execute("init-readonly", ["init", "-lockfile=readonly", "-input=false", "-no-color"])
        if (copied / LOCK_NAME).read_bytes() != candidate:
            raise RuntimeError("Readonly initialization changed the candidate lock; no learner lock was written.")
        changed = original is None or candidate != original["content"]
        written = False
        if write and changed:
            publish_lock(original_path, candidate, original, configuration, lab, setup_bytes, run_directory)
            written = True
        record.update(result="passed", changed=changed, written=written,
                      candidate_sha256=hashlib.sha256(candidate).hexdigest())
        print(f"Verified simulator lock for {setup['platform']}: changed={changed}, written={written}.")
        if changed and not write:
            print("Dry run preserved the learner lock. Review the private candidate; rerun with --write to publish after verification.")
        print(f"Private evidence: {run_directory}")
        return record
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        record.update(result="failed", error=str(error), written=False)
        raise
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_directory / "summary.json").write_text(json.dumps(record, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", type=Path, nargs="?", default=ROOT / "labs/05-simulator-resource-group")
    parser.add_argument("--write", action="store_true", help="Back up and publish the verified lock if changed; otherwise dry-run.")
    args = parser.parse_args()
    try:
        reconcile(args.lab, args.write)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Simulator lock verification failed: {error}\n")


if __name__ == "__main__":
    main()
