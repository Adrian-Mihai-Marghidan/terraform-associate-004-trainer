#!/usr/bin/env python3
"""Check package consistency. This does not parse HCL or run Terraform."""
import json
import os
import re
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(root):
    root = Path(root).resolve()
    data = json.loads((root / "docs/objectives.json").read_text())
    rows = data["objectives"]
    expected = {f"{domain}{chr(97 + i)}" for domain, n in enumerate((3,4,7,8,4,4,3,4), 1) for i in range(n)}
    ids = [row["id"] for row in rows]
    require(data["exam"] == "004", "Objective map differs from the agreed Associate 004 target")
    require(data["terraform_version"] == "1.12", "Objective map differs from the agreed Terraform 1.12 target")
    require(len(ids) == len(set(ids)) == 37, "Duplicate or missing objective rows")
    require(set(ids) == expected, "Objective IDs differ from the 004 map")
    progress = json.loads((root / "templates/PROGRESS.json").read_text())
    require([o["id"] for o in progress["objectives"]] == ids, "Progress objective map drift")
    require([(o["id"], o["lesson"]) for o in progress["objectives"]]
            == [(row["id"], row["lesson"]) for row in rows], "Progress lesson map drift")
    require(progress["exam_target"] == f"Terraform Associate {data['exam']}", "Progress exam target drift")
    require(progress["exam_terraform_version"] == data["terraform_version"], "Progress Terraform version drift")
    require(progress["current_lesson"] == "00.1", "Default lesson must start at foundations")
    curriculum = (root / "docs/CURRICULUM.md").read_text()
    for row in rows:
        require(f'| {row["lesson"]} |' in curriculum, f'Missing lesson for {row["id"]}')
    public_files = []
    for directory, children, filenames in os.walk(root):
        children[:] = [name for name in children if name not in {".git", "private", ".tools", ".terraform", ".simulator", "__pycache__"}]
        public_files.extend(Path(directory) / name for name in filenames)
    for source in (path for path in public_files if path.suffix == ".md"):
        body = source.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", body):
            if target.startswith(("http://", "https://", "#")):
                continue
            path = source.parent / target.split("#", 1)[0]
            require(path.exists(), f"Broken link in {source.relative_to(root)}: {target}")
    for source in (root / "templates").glob("*.json"):
        json.loads(source.read_text())
    skill = root / ".agents/skills/terraform-certification-tutor/SKILL.md"
    text = skill.read_text()
    require(text.startswith("---\nname: terraform-certification-tutor\n"), "Invalid skill header")
    require("description:" in text.split("---", 2)[1], "Missing skill trigger")
    for source in (path for path in public_files if path.suffix == ".tf"):
        require("azurerm_" not in source.read_text(), "Starter labs should stay local")
        require("hashicorp/azurerm" not in source.read_text(), "Simulator labs must never select AzureRM")
    for directory in ("labs/05-simulator-resource-group", "tests/fixtures/simulator-resource-group"):
        versions = (root / directory / "versions.tf").read_text()
        require('source  = "terraform.local/learning/azuresim"' in versions,
                f"Missing distinct simulator source in {directory}")
        require('version = "= 0.1.1"' in versions, f"Missing simulator version pin in {directory}")
    require((root / "docs/SIMULATOR_INTEGRATION.md").is_file(), "Missing required integration contract")
    require((root / "labs/04-terraform-test/tests/environment.tftest.hcl").exists(), "Missing optional test")
    print("Package checks passed: 37 objectives, mapped lessons, records, simulator contract, and local links.")
    print("Terraform HCL syntax, runtime behavior, and actual Codex discovery are separate checks.")

if __name__ == "__main__":
    check(Path(__file__).resolve().parents[1])
