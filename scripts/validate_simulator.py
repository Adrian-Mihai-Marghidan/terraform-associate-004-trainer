#!/usr/bin/env python3
"""Execute the Resource Group milestone in a private disposable agent lab."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "terraform.local/learning/azuresim"
ADDRESS = "azuresim_resource_group.lesson"


def main():
    setup = json.loads((ROOT / "private/SIMULATOR_SETUP.json").read_text())
    base = ROOT / "private/development/validation"
    base.mkdir(parents=True, exist_ok=True)
    lab = Path(tempfile.mkdtemp(prefix="resource-group-", dir=base))
    logs = lab / "evidence"
    logs.mkdir()
    fixture = ROOT / "tests/fixtures/simulator-resource-group"
    for file in fixture.glob("*.tf"):
        shutil.copyfile(file, lab / file.name)
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("TF_CLI_ARGS") and key not in ("TF_DATA_DIR", "TF_WORKSPACE", "TF_PLUGIN_CACHE_DIR")}
    env.update(TF_CLI_CONFIG_FILE=setup["cli_config"], CHECKPOINT_DISABLE="1", TF_IN_AUTOMATION="1")
    env["PATH"] = str(Path(setup["terraform_binary"]).parent) + os.pathsep + str(Path(setup["simctl_binary"]).parent) + os.pathsep + env["PATH"]
    terraform, simctl = setup["terraform_binary"], setup["simctl_binary"]
    checks = []

    def run(label, command, expected=0, cwd=lab):
        print(f"{label}: {' '.join(str(part) for part in command)}", flush=True)
        result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
        (logs / f"{label}.log").write_text(result.stdout + result.stderr)
        checks.append({"check": label, "command": [str(part) for part in command],
                       "cwd": str(cwd), "exit_code": result.returncode, "expected_exit_code": expected})
        if result.returncode != expected:
            print(result.stdout + result.stderr, flush=True)
            raise RuntimeError(f"{label}: expected exit {expected}, got {result.returncode}; evidence {logs}")
        return result.stdout

    def tf(label, *args, expected=0):
        return run(label, [terraform, *args], expected)

    def plan(label, expected, refresh_only=False):
        args = ["plan", "-input=false", "-no-color", "-detailed-exitcode", f"-out={label}.tfplan"]
        if refresh_only:
            args.append("-refresh-only")
        tf(label, *args, expected=expected)
        return json.loads(tf(label + "-json", "show", "-json", f"{label}.tfplan"))

    def change(document):
        return next(row for row in document["resource_changes"] if row["address"] == ADDRESS)["change"]

    def infrastructure():
        return json.loads((lab / ".simulator/infrastructure.json").read_text())["resource_groups"]

    def require(condition, message):
        if not condition:
            raise RuntimeError(message)

    record = {"kind": "agent-development-validation", "learner_evidence": False,
              "started_at": datetime.now(ZoneInfo("Europe/Bucharest")).isoformat(),
              "timezone": "Europe/Bucharest", "lab": str(lab), "setup": setup, "checks": checks}
    try:
        version = json.loads(tf("version", "version", "-json"))
        require(version["terraform_version"].startswith("1.12."), 'Validation failed: version["terraform_version"].startswith("1.12.")')
        run("startup", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(lab)])
        tf("init", "init", "-input=false", "-no-color")
        tf("fmt", "fmt", "-check")
        tf("validate", "validate", "-no-color")
        schema = json.loads(tf("schema", "providers", "schema", "-json"))
        require(set(schema["provider_schemas"]) == {SOURCE}, 'Validation failed: set(schema["provider_schemas"]) == {SOURCE}')
        require(set(schema["provider_schemas"][SOURCE]["resource_schemas"]) == {"azuresim_resource_group"}, 'Validation failed: set(schema["provider_schemas"][SOURCE]["resource_schemas"]) == {"azuresim_resource_group"}')
        created = plan("create-plan", 2)
        require(change(created)["actions"] == ["create"], 'Validation failed: change(created)["actions"] == ["create"]')
        require(not (lab / ".simulator/infrastructure.json").exists(), "Plan created simulated infrastructure")
        tf("create-apply", "apply", "-input=false", "-no-color", "create-plan.tfplan")
        require(tf("state-list", "state", "list").strip() == ADDRESS, 'Validation failed: tf("state-list", "state", "list").strip() == ADDRESS')
        groups = infrastructure()
        require(len(groups) == 1, 'Validation failed: len(groups) == 1')
        resource_id = next(iter(groups))
        require(groups[resource_id]["tags"] == {"environment": "learning"}, 'Validation failed: groups[resource_id]["tags"] == {"environment": "learning"}')
        require((lab / "terraform.tfstate").resolve() != (lab / ".simulator/infrastructure.json").resolve(), 'Validation failed: (lab / "terraform.tfstate").resolve() != (lab / ".simulator/infrastructure.json").resolve()')
        run("startup-with-state", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(lab)])
        # Valid comments must not be mistaken for backend/provider declarations.
        config = lab / "main.tf"
        config.write_text(config.read_text() + "\n# Local backend; no real cloud resources or azurerm provider.\n")
        run("startup-harmless-comments", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(lab)])
        bypass = lab / "blocked-wrong-storage"
        bypass.mkdir()
        for file in lab.glob("*.tf"):
            shutil.copyfile(file, bypass / file.name)
        expression = 'storage_path = "${abspath(path.root)}/.simulator/infrastructure.json"'
        wrong_config = bypass / "main.tf"
        wrong_config.write_text(wrong_config.read_text().replace(expression, 'storage_path = "/tmp/unrelated-store.json"')
                                + f"\n# {expression}\n")
        run("blocked-comment-storage-bypass", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(bypass)], expected=1)
        wrong_config.write_text(config.read_text().replace(expression,
            'storage_path = path.root == "." ? "/tmp/unrelated-store.json" : "${abspath(path.root)}/.simulator/infrastructure.json"'))
        run("blocked-conditional-storage-bypass", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(bypass)], expected=1)
        workspace = lab / "blocked-workspace"
        workspace.mkdir()
        for file in lab.glob("*.tf"):
            shutil.copyfile(file, workspace / file.name)
        (workspace / ".terraform").mkdir()
        (workspace / ".terraform/environment").write_text("other")
        named_state = workspace / "terraform.tfstate.d/other/terraform.tfstate"
        named_state.parent.mkdir(parents=True)
        named_state.write_text(json.dumps({"version": 4, "resources": [
            {"provider": 'provider["registry.terraform.io/hashicorp/azurerm"]'}]}))
        run("blocked-named-workspace", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(workspace)], expected=1)
        require("default Terraform workspace" in (logs / "blocked-named-workspace.log").read_text(), "Named workspace was not explicitly rejected")
        blocked_state = lab / "blocked-state-provider"
        blocked_state.mkdir()
        for file in lab.glob("*.tf"):
            shutil.copyfile(file, blocked_state / file.name)
        foreign_state = json.loads((lab / "terraform.tfstate").read_text())
        foreign_state["resources"][0]["provider"] = 'provider["registry.terraform.io/hashicorp/azurerm"]'
        (blocked_state / "terraform.tfstate").write_text(json.dumps(foreign_state))
        run("blocked-state-provider", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(blocked_state)], expected=1)
        require("Unexpected providers" in (logs / "blocked-state-provider.log").read_text(), 'Validation failed: "Unexpected providers" in (logs / "blocked-state-provider.log").read_text()')
        plan("unchanged-plan", 0)

        storage = lab / ".simulator/infrastructure.json"
        valid_storage = storage.read_bytes()
        storage.write_text("{}")
        tf("corrupt-store-plan", "plan", "-input=false", "-no-color", expected=1)
        require(storage.read_bytes() == b"{}", "Terraform overwrote malformed infrastructure")
        run("corrupt-store-mutation", [simctl, "set-tags", "--storage", str(storage),
                                      "--name", "mentor-rg", "--tags", '{"environment":"external"}'], expected=1)
        require(storage.read_bytes() == b"{}", "simctl overwrote malformed infrastructure")
        storage.write_bytes(valid_storage)

        config = lab / "main.tf"
        original = config.read_text()
        updated = original.replace('environment = "learning"', 'environment = "practice"')
        require(updated != original, 'Validation failed: updated != original')
        config.write_text(updated)
        update = plan("tag-update-plan", 2)
        require(change(update)["actions"] == ["update"], 'Validation failed: change(update)["actions"] == ["update"]')
        tf("tag-update-apply", "apply", "-input=false", "-no-color", "tag-update-plan.tfplan")
        require(infrastructure()[resource_id]["tags"] == {"environment": "practice"}, 'Validation failed: infrastructure()[resource_id]["tags"] == {"environment": "practice"}')
        plan("updated-unchanged-plan", 0)

        state_before = (lab / "terraform.tfstate").read_bytes()
        run("external-tags", [simctl, "set-tags", "--storage", str(lab / ".simulator/infrastructure.json"),
                              "--name", "mentor-rg", "--tags", '{"environment":"external"}'])
        require((lab / "terraform.tfstate").read_bytes() == state_before, "External operation edited Terraform state")
        drift = plan("drift-plan", 2)
        require(change(drift)["actions"] == ["update"], 'Validation failed: change(drift)["actions"] == ["update"]')
        require(change(drift)["before"]["tags"] == {"environment": "external"}, 'Validation failed: change(drift)["before"]["tags"] == {"environment": "external"}')
        require(change(drift)["after"]["tags"] == {"environment": "practice"}, 'Validation failed: change(drift)["after"]["tags"] == {"environment": "practice"}')
        require(any(row["address"] == ADDRESS for row in drift["resource_drift"]), 'Validation failed: any(row["address"] == ADDRESS for row in drift["resource_drift"])')
        refresh = plan("refresh-only-plan", 2, refresh_only=True)
        require(not [row for row in refresh.get("resource_changes", []) if row["change"]["actions"] != ["no-op"]], 'Validation failed: not [row for row in refresh.get("resource_changes", []) if row["change"]["actions"] != ["no-op"]]')
        require(infrastructure()[resource_id]["tags"] == {"environment": "external"}, 'Validation failed: infrastructure()[resource_id]["tags"] == {"environment": "external"}')
        tf("drift-reconcile", "apply", "-input=false", "-no-color", "drift-plan.tfplan")
        require(infrastructure()[resource_id]["tags"] == {"environment": "practice"}, 'Validation failed: infrastructure()[resource_id]["tags"] == {"environment": "practice"}')
        plan("reconciled-plan", 0)

        # Verify documented replacement planning and provider diagnostics.
        config.write_text(updated.replace('name     = "mentor-rg"', 'name     = "renamed-rg"'))
        replacement = plan("rename-plan", 2)
        require(sorted(change(replacement)["actions"]) == ["create", "delete"], 'Validation failed: sorted(change(replacement)["actions"]) == ["create", "delete"]')
        tf("rename-apply", "apply", "-input=false", "-no-color", "rename-plan.tfplan")
        require(next(iter(infrastructure().values()))["name"] == "renamed-rg", "Rename replacement did not persist")
        plan("renamed-unchanged-plan", 0)
        config.write_text(updated)
        plan("restore-name-plan", 2)
        tf("restore-name-apply", "apply", "-input=false", "-no-color", "restore-name-plan.tfplan")
        config.write_text(updated.replace('name     = "mentor-rg"', 'name     = "bad/name"'))
        tf("invalid-name", "validate", "-no-color", expected=1)
        config.write_text(updated)

        # Provider Read must expose deletion as absence rather than a diagnostic.
        run("external-delete", [simctl, "delete", "--storage", str(lab / ".simulator/infrastructure.json"), "--name", "mentor-rg"])
        missing = plan("missing-plan", 2)
        require(change(missing)["actions"] == ["create"], 'Validation failed: change(missing)["actions"] == ["create"]')
        tf("missing-recreate", "apply", "-input=false", "-no-color", "missing-plan.tfplan")

        blocked = lab / "blocked-real-provider"
        blocked.mkdir()
        (blocked / "main.tf").write_text('terraform {\n  required_providers {\n    azurerm = {\n      source = "hashicorp/azurerm"\n    }\n  }\n}\n')
        run("blocked-startup-provider", [sys.executable, str(ROOT / "scripts/check_simulator.py"), str(blocked)], expected=1)
        run("blocked-real-provider", [terraform, "init", "-input=false", "-no-color"], expected=1, cwd=blocked)
        # The recorded stderr identifies the local mirror failure; no fallback is present.
        require(not (blocked / ".terraform/providers/registry.terraform.io/hashicorp/azurerm").exists(), 'Validation failed: not (blocked / ".terraform/providers/registry.terraform.io/hashicorp/azurerm").exists()')

        tf("destroy", "destroy", "-auto-approve", "-input=false", "-no-color")
        require(infrastructure() == {}, 'Validation failed: infrastructure() == {}')
        require(tf("empty-state", "state", "list").strip() == "", 'Validation failed: tf("empty-state", "state", "list").strip() == ""')
        require(json.loads(run("empty-storage", [simctl, "list", "--storage", str(lab / ".simulator/infrastructure.json")])) == [], 'Validation failed: json.loads(run("empty-storage", [simctl, "list", "--storage", str(lab / ".simulator/infrastructure.json")])) == []')
        record.update(result="passed", terraform_version=version["terraform_version"],
                      provider_sha256=hashlib.sha256(Path(setup["provider_binary"]).read_bytes()).hexdigest(),
                      verified_behaviors=["init", "validate", "plan", "create", "no-op", "tag-update",
                                          "external-tag-drift", "refresh-only-plan", "reconcile", "rename-replacement-apply",
                                          "invalid-name-diagnostic", "external-deletion", "blocked-AzureRM-install",
                                          "malformed-storage-preservation", "startup-guard-regressions", "destroy"])
        print(f"Resource Group milestone passed. Private evidence: {logs}")
    except Exception as error:
        record.update(result="failed", error=str(error))
        raise
    finally:
        record["finished_at"] = datetime.now(ZoneInfo("Europe/Bucharest")).isoformat()
        (logs / "summary.json").write_text(json.dumps(record, indent=2) + "\n")
        (ROOT / "private/development/LAST_SIMULATOR_VALIDATION.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()
