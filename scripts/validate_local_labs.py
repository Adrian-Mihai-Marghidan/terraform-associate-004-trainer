#!/usr/bin/env python3
"""Run supplemental lab checks in private agent copies, never learner state."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BUILTIN = "terraform.io/builtin/terraform"
SIMULATOR = "terraform.local/learning/azuresim"
LABS = {
    "00-first-run": {
        "addresses": ["terraform_data.example"],
        "outputs": {"message": "My first Terraform resource"},
    },
    "01-variables": {
        "addresses": ["terraform_data.environment"],
        "outputs": {"label": "mentor-dev"},
    },
    "02-for-each": {
        "addresses": ['terraform_data.service["api"]', 'terraform_data.service["web"]'],
        "outputs": {
            "service_details": {
                "api": {"name": "api", "tier": "backend"},
                "web": {"name": "web", "tier": "frontend"},
            }
        },
    },
    "03-modules": {
        "addresses": ["module.service.terraform_data.service"],
        "outputs": {"service_details": {"name": "api", "environment": "dev"}},
    },
    "04-terraform-test": {"test_runs": ["normalizes_case", "rejects_invalid_environment"]},
}


def timestamp():
    return datetime.now(ZoneInfo("Europe/Bucharest")).isoformat()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def configuration_files(source):
    """Include Terraform source and dependency locks, excluding runtime trees."""
    ignored = {".terraform", ".simulator", "__pycache__"}
    return sorted(
        file for file in source.rglob("*")
        if file.is_file()
        and not ignored.intersection(file.relative_to(source).parts)
        and (file.name.endswith((".tf", ".tftest.hcl")) or file.name == ".terraform.lock.hcl")
    )


def snapshot(source):
    return {str(file.relative_to(source)): hashlib.sha256(file.read_bytes()).hexdigest()
            for file in configuration_files(source)}


def resources(values):
    def walk(module):
        result = list(module.get("resources", []))
        for child in module.get("child_modules", []):
            result.extend(walk(child))
        return result
    return [row for row in walk(values.get("root_module", {})) if row["mode"] == "managed"]


def validate_lab(name, expectations, base, terraform, env):
    source = ROOT / "labs" / name
    lab = base / name
    lab.mkdir()
    before = snapshot(source)
    for file in configuration_files(source):
        if file.is_symlink():
            raise ValueError(f"Refusing symlinked lab configuration: {file}")
        target = lab / file.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
    logs = lab / "evidence"
    logs.mkdir()
    record = {"lab": name, "source": str(source), "agent_lab": str(lab),
              "learner_evidence": False, "started_at": timestamp(), "checks": [],
              "source_sha256": before, "verified_behaviors": []}

    def run(label, *args, expected=0):
        command = [str(terraform), *args]
        print(f"{name}/{label}", flush=True)
        result = subprocess.run(command, cwd=lab, env=env, text=True, capture_output=True,
                                timeout=120)
        (logs / f"{label}.log").write_text(result.stdout + result.stderr)
        record["checks"].append({"check": label, "command": command, "cwd": str(lab),
                                 "exit_code": result.returncode, "expected_exit_code": expected})
        if result.returncode != expected:
            raise RuntimeError(f"{label}: expected exit {expected}, got {result.returncode}; "
                               f"see {logs / (label + '.log')}")
        return result.stdout

    def plan(label, expected, *arguments):
        run(label, "plan", "-input=false", "-no-color", "-detailed-exitcode",
            f"-out={label}.tfplan", *arguments, expected=expected)
        return json.loads(run(label + "-json", "show", "-json", f"{label}.tfplan"))

    try:
        run("init", "init", "-input=false", "-no-color")
        run("fmt", "fmt", "-check", "-recursive")
        run("validate", "validate", "-no-color")
        providers = run("providers", "providers")
        identities = set(re.findall(r"provider\[([^]]+)\]", providers))
        require(identities <= {BUILTIN}, f"Unexpected provider identities: {sorted(identities)}")
        record["provider_sources"] = sorted(identities)
        record["verified_behaviors"].extend(["init", "fmt", "validate", "built-in-only"])

        if "test_runs" in expectations:
            output = run("test", "test", "-no-color")
            require("Success! 2 passed, 0 failed." in output, "Expected both test runs to pass")
            for test_run in expectations["test_runs"]:
                require(re.search(r'run "' + re.escape(test_run) + r'"\.\.\. pass', output),
                        f"Expected test run to pass: {test_run}")
            require(not (lab / "terraform.tfstate").exists(), "Plan-only tests wrote learner-style state")
            record["verified_behaviors"].extend(["case-normalization-test", "expected-validation-failure-test",
                                                  "plan-only-no-persistent-state"])
        else:
            addresses = expectations["addresses"]
            creation = plan("create-plan", 2)
            changes = {row["address"]: row["change"]["actions"]
                       for row in creation.get("resource_changes", [])}
            require(changes == {address: ["create"] for address in addresses},
                    f"Unexpected creation actions: {changes}")
            require(not (lab / "terraform.tfstate").exists(), "Creation plan unexpectedly wrote state")
            run("apply", "apply", "-input=false", "-no-color", "create-plan.tfplan")
            require(run("state-list", "state", "list").splitlines() == sorted(addresses),
                    "Unexpected Terraform state addresses")
            state = json.loads(run("state-json", "show", "-json"))
            state_resources = resources(state.get("values", {}))
            require(len(state_resources) == len(addresses), "Unexpected managed resource count")
            require(all(row["provider_name"] == BUILTIN for row in state_resources),
                    "An unexpected provider created a managed resource")
            outputs = json.loads(run("outputs", "output", "-json"))
            observed = {key: row["value"] for key, row in outputs.items()}
            require(observed == expectations["outputs"], f"Unexpected output values: {observed}")
            unchanged = plan("unchanged-plan", 0)
            require(all(row["change"]["actions"] == ["no-op"]
                        for row in unchanged.get("resource_changes", [])),
                    "Repeated plan unexpectedly proposes resource changes")
            record.update(managed_resource_count=len(state_resources), verified_outputs=observed)
            record["verified_behaviors"].extend(["genuine-create-plan", "apply", "state-addresses",
                                                  "resource-count", "outputs", "no-change-plan"])

            state_before = (lab / "terraform.tfstate").read_bytes()
            if name == "01-variables":
                changed = plan("variable-change-plan", 2, "-var=environment=test")
                change = next(row["change"] for row in changed["resource_changes"]
                              if row["address"] == addresses[0])
                require(change["actions"] == ["update"] and change["after"]["input"] == "mentor-test",
                        "A valid variable change did not plan the expected input update")
                run("invalid-variable", "plan", "-input=false", "-no-color",
                    "-var=environment=invalid", expected=1)
                require("Choose dev, test, or prod." in (logs / "invalid-variable.log").read_text(),
                        "Missing expected invalid-variable diagnostic")
                record["verified_behaviors"].extend(["variable-update-plan", "invalid-variable-diagnostic"])
            elif name == "02-for-each":
                changed = plan("remove-key-plan", 2, '-var=services={"api":{"tier":"backend"}}')
                actions = {row["address"]: row["change"]["actions"]
                           for row in changed["resource_changes"]}
                require(actions == {addresses[0]: ["no-op"], addresses[1]: ["delete"]},
                        f"Unexpected stable-key removal actions: {actions}")
                record["verified_behaviors"].append("stable-key-removal-plan")
            require((lab / "terraform.tfstate").read_bytes() == state_before,
                    "Plans modified persisted state")
            run("destroy", "destroy", "-auto-approve", "-input=false", "-no-color")
            require(run("empty-state", "state", "list").strip() == "",
                    "Terraform state still contains resources after destroy")
            require(resources(json.loads(run("destroyed-state-json", "show", "-json")).get("values", {})) == [],
                    "Managed resources remain in JSON state after destroy")
            record["verified_behaviors"].append("destroy-empty-state")
        require(snapshot(source) == before, "Original learner configuration changed during validation")
        record.update(result="passed", learner_configuration_preserved=True)
        print(f"{name}: passed", flush=True)
    except Exception as error:
        record.update(result="failed", error=str(error))
        print(f"{name}: failed: {error}", flush=True)
        # Cleanup is confined to the disposable agent copy, including after a failed check.
        if (lab / "terraform.tfstate").exists():
            try:
                run("failure-cleanup", "destroy", "-auto-approve", "-input=false", "-no-color")
            except Exception as cleanup_error:
                record["cleanup_error"] = str(cleanup_error)
    finally:
        record["finished_at"] = timestamp()
        (logs / "summary.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main():
    setup = json.loads((ROOT / "private/SIMULATOR_SETUP.json").read_text())
    terraform = Path(setup["terraform_binary"])
    base_root = ROOT / "private/development/local-labs-validation"
    base_root.mkdir(parents=True, exist_ok=True)
    base = Path(tempfile.mkdtemp(prefix="run-", dir=base_root))
    # No Terraform environment overrides or external provider registry fallback.
    env = {key: value for key, value in os.environ.items() if not key.startswith("TF_")}
    cli_config = base / "simulator-only.tfrc"
    cli_config.write_text("disable_checkpoint = true\nprovider_installation {\n"
                          "  filesystem_mirror {\n"
                          f"    path = {json.dumps(str(ROOT / '.tools/provider-mirror'))}\n"
                          f"    include = [{json.dumps(SIMULATOR)}]\n  }}\n}}\n")
    env.update(TF_CLI_CONFIG_FILE=str(cli_config), TF_IN_AUTOMATION="1", TF_INPUT="0", CHECKPOINT_DISABLE="1")
    record = {"kind": "agent-development-validation", "learner_evidence": False,
              "started_at": timestamp(), "timezone": "Europe/Bucharest", "run_directory": str(base),
              "terraform_binary": str(terraform), "cli_config": str(cli_config), "labs": []}
    try:
        command = [str(terraform), "version", "-json"]
        result = subprocess.run(command, cwd=base, env=env, text=True, capture_output=True, timeout=30)
        (base / "version.log").write_text(result.stdout + result.stderr)
        record["version_check"] = {"command": command, "cwd": str(base), "exit_code": result.returncode}
        if result.returncode:
            raise RuntimeError(f"Terraform version check failed; see {base / 'version.log'}")
        version = json.loads(result.stdout)
        if version["terraform_version"] != "1.12.2":
            raise ValueError("This validation expects the documented isolated Terraform 1.12.2.")
        record.update(terraform_version=version["terraform_version"], platform=version["platform"])
        for name, expectations in LABS.items():
            record["labs"].append(validate_lab(name, expectations, base, terraform, env))
        record["result"] = "passed" if all(lab["result"] == "passed" for lab in record["labs"]) else "failed"
    except Exception as error:
        record.update(result="failed", error=str(error))
        print(f"Local lab validation failed: {error}", flush=True)
    finally:
        record["finished_at"] = timestamp()
        body = json.dumps(record, indent=2) + "\n"
        (base / "summary.json").write_text(body)
        (ROOT / "private/development/LAST_LOCAL_LABS_VALIDATION.json").write_text(body)
    print(f"Local lab validation {record['result']}. Private evidence: {base}", flush=True)
    return 0 if record["result"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
