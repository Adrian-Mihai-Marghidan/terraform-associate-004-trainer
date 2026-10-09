#!/usr/bin/env python3
"""Check a simulator lab before Terraform operations; never plan or apply."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "terraform.local/learning/azuresim"


def check(lab):
    lab = Path(lab).resolve()
    setup_path = ROOT / "private/SIMULATOR_SETUP.json"
    if not setup_path.is_file():
        raise ValueError("Run scripts/setup_simulator.py, then source private/simulator-env.sh.")
    setup = json.loads(setup_path.read_text())
    if os.environ.get("TF_CLI_CONFIG_FILE") != setup["cli_config"]:
        raise ValueError("Source private/simulator-env.sh in this terminal; TF_CLI_CONFIG_FILE differs.")
    for name in os.environ:
        if name.startswith("TF_CLI_ARGS") or name in ("TF_DATA_DIR", "TF_WORKSPACE", "TF_PLUGIN_CACHE_DIR"):
            raise ValueError(f"Unset {name} for the isolated simulator lab.")
    terraform = shutil.which("terraform")
    if not terraform or Path(terraform).resolve() != Path(setup["terraform_binary"]).resolve():
        raise ValueError("The active Terraform differs from the isolated CLI. Source the simulator environment.")
    version = json.loads(subprocess.check_output([terraform, "version", "-json"]))
    if not version["terraform_version"].startswith("1.12."):
        raise ValueError("Terraform 1.12.x is required; do not silently upgrade or downgrade.")
    mirror = ROOT / ".tools/provider-mirror"
    expected_config = ("disable_checkpoint = true\nprovider_installation {\n  filesystem_mirror {\n"
                       f"    path = {json.dumps(str(mirror))}\n    include = [{json.dumps(SOURCE)}]\n  }}\n}}\n")
    if Path(setup["cli_config"]).read_text() != expected_config:
        raise ValueError("Simulator CLI configuration changed; restore its local-only mirror via setup.")
    binary = Path(setup["provider_binary"])
    if not binary.is_file() or hashlib.sha256(binary.read_bytes()).hexdigest() != setup["provider_sha256"]:
        raise ValueError("Simulator provider is absent or changed; rebuild setup and reconcile its lab lock file.")
    simctl = Path(setup["simctl_binary"])
    if not simctl.is_file() or hashlib.sha256(simctl.read_bytes()).hexdigest() != setup.get("simctl_sha256"):
        raise ValueError("Simulator control tool is absent or changed; run setup before practice.")
    if not lab.is_dir() or not list(lab.glob("*.tf")):
        raise ValueError("Choose a simulator Terraform lab directory.")
    workspace_file = lab / ".terraform/environment"
    if workspace_file.exists() and workspace_file.read_text().strip() != "default":
        raise ValueError("Use the default Terraform workspace in this starter lab; preserve other workspace state.")
    # Parse actual HCL blocks and the provider attribute, not words in comments.
    inspected = subprocess.run([str(simctl), "check-lab", "--lab", str(lab)], text=True, capture_output=True)
    if inspected.returncode:
        raise ValueError(inspected.stderr.strip() or inspected.stdout.strip())
    storage = Path(json.loads(inspected.stdout)["storage_path"])
    expected_storage = lab / ".simulator/infrastructure.json"
    if storage != expected_storage or (lab / ".simulator").is_symlink() or storage.is_symlink():
        raise ValueError("Use a separate per-lab .simulator directory without storage symlinks.")
    # Inspect configuration with Terraform itself, without requiring learner init.
    # A generated lock may exist before .terraform/providers is populated.
    with tempfile.TemporaryDirectory(prefix="azuresim-preflight-") as directory:
        preview = Path(directory)
        for file in lab.glob("*.tf"):
            shutil.copyfile(file, preview / file.name)
        result = subprocess.run([terraform, f"-chdir={preview}", "providers"], text=True, capture_output=True)
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    sources = set(re.findall(r"provider\[([^]]+)\]", result.stdout))
    selected = re.search(r"provider\[" + re.escape(SOURCE) + r"\] ([^\n]+)", result.stdout)
    if not selected or selected.group(1).strip() != setup["provider_version"]:
        raise ValueError(f"Pin the starter lab to simulator {setup['provider_version']}; preserve state and reconcile its lock deliberately.")
    state_path = lab / "terraform.tfstate"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state.get("version") != 4:
            raise ValueError("Unexpected Terraform state format; preserve it and investigate before simulator practice.")
        for instance in state.get("resources", []):
            match = re.search(r'provider\["([^"]+)"\]', instance.get("provider", ""))
            if not match:
                raise ValueError("Unrecognized provider identity in state; preserve it and investigate.")
            sources.add(match.group(1))
    if SOURCE not in sources or sources - {SOURCE, "terraform.io/builtin/terraform"}:
        raise ValueError(f"Unexpected providers in configuration or state: {sorted(sources)}")
    if storage.resolve() == (lab / "terraform.tfstate").resolve():
        raise ValueError("Simulator storage must be separate from Terraform state.")
    subprocess.run([setup["simctl_binary"], "list", "--storage", str(storage)], check=True, stdout=subprocess.DEVNULL)
    print(f"Startup checks passed: Terraform {version['terraform_version']}, azuresim {setup['provider_version']}, local storage, isolated lab.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", type=Path)
    args = parser.parse_args()
    try:
        check(args.lab)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Simulator startup check failed: {error}\n")
