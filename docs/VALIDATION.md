# Validation record

Date: 2026-10-10, Europe/Bucharest.

## Simulator milestone and regressions: passed

The independent sibling simulator is version **0.1.1**, built with Go 1.27.2, Terraform Plugin Framework 1.15.1, and the official HCL v2.24.0 parser.
The actual Terraform CLI was **1.12.2 on darwin_arm64**, isolated under ignored .tools. Setup leaves global Terraform installations unchanged.

The latest run executed 51 recorded command checks in a fresh private disposable lab copied from tests/fixtures/simulator-resource-group. It used no learner configuration, state, storage, or lock.
Executed:

- Simulator-only filesystem-mirror installation with terraform init, then fmt -check and validate.
- Genuine creation plan/apply; one Resource Group persisted in separate JSON infrastructure storage.
- State inspection, expected resource identity/tags, and repeated unchanged plans.
- Tag-update plan/apply with a confirmed in-place storage update.
- Out-of-band tag changes leaving Terraform state bytes unchanged; real drift detection, refresh-only planning, and reconciliation.
- Name replacement plan/apply, unchanged plan for the renamed resource, and replacement back to the original name.
- Invalid-name diagnostics and out-of-band deletion followed by recreation.
- Startup before init and with real local state; harmless comments accepted.
- Rejection of commented and conditional storage-path bypasses, a named workspace containing foreign provider state, and AzureRM state identities.
- Existing malformed storage rejected by real Terraform planning and simctl mutation with its bytes preserved.
- AzureRM installation blocked by the simulator-only mirror with no registry fallback.
- Destroy, empty simulated storage, and an empty Terraform resource-state list.

Maintainer runtime evidence is generated locally under ignored private/development/validation. private/development/LAST_SIMULATOR_VALIDATION.json points to the latest local run and records actual commands, exit codes, timestamps, and setup hashes. Raw logs and plans are intentionally absent from public Git; rerun the validator against the compatible source to produce your own evidence.

The final sibling build/tests and Go race tests passed for storage and preflight. Regressions include missing/null schema/resource/tag fields, malformed tag values, unknown/trailing JSON, concurrent writes, storage spoofing, aliases, foreign sources/resources, modules, backend/cloud, data/ephemeral sources, JSON/overrides, and relative/conditional path.root behavior.
The provider checksum was identical when built from staging and the final sibling path. Installed 0.1.0 remains preserved; 0.1.1 was installed separately.
The committed starter lock records the verified native macOS arm64 package. Other platforms require verified packages and deliberate lock reconciliation. Starter preflight was also checked against the shipped learner configuration without applying it; individual learner state and execution status are not published.

Sandbox DNS initially blocked dependency downloads; approved setup downloaded the pinned dependencies and passed. Provider IPC was previously blocked by sandbox execution, so the final full simulator runtime check used approved execution outside the sandbox. No unresolved execution blocker remains on the verified host. No Azure authentication or provisioning occurred.

## Supplemental local labs: passed

scripts/validate_local_labs.py passed normally and under python3 -O. The latest run executed 71 actual Terraform commands in private copies of all five supplemental labs:

- 00-first-run, 01-variables, 02-for-each, and 03-modules: init, recursive formatting, validate, genuine create plans/apply, exact state addresses/counts/outputs, unchanged plans, and destroy with empty resource state.
- Variables: valid update planning and invalid-value diagnostics.
- for_each: removing one key planned deletion for that instance and retained the other address.
- Optional 04-terraform-test: both plan-only runs passed (2 passed, 0 failed), with no persistent state.

Maintainer evidence is generated locally under ignored private/development/local-labs-validation; private/development/LAST_LOCAL_LABS_VALIDATION.json points to the latest local run. Original learner configurations were verified unchanged. A public clone includes reproduction scripts, not another learner's records.

## Package, installation, and skill checks: passed

- 42 Python regression tests passed. They cover tool mismatch preservation, interrupted downloads, offline caches, staged installation, immutable packages, backup retention, objective-map drift, non-overwriting timezone setup, actual indexed public-content checks, and safe provider-lock reconciliation.
- Current isolated tools were verified from actual version/platform output. A fresh disposable installation from checksum-verified cached archives passed with network access explicitly disabled.
- Package checks passed normally and under optimization for all 37 objective IDs, ID-to-lesson mappings, exam/version targets, templates, local links, skill metadata, and simulator pins.
- Python compilation and the tutor Skill Creator validator passed.
- Git ignore checks exclude private records, toolchains, stores, state, plans, logs, environment files, and credential keys; the provider lock remains eligible.

Runtime and package validators raise explicit errors; Python optimization cannot disable their semantic checks.

## Pending or unsupported

Linux/WSL2 and other platforms have not had runtime execution verified here.
Only Resource Groups are implemented. Simulator data sources/import, additional Azure types, Azure service fidelity, remote backend behavior, Vault provider features, and HCP need explicit separate exercises or official explanations.
Starter preflight permits one unaliased provider and default workspace; later alias/module exercises need their own guarded configuration contract.
Actual learner skill-selector discovery, teaching, independent execution, delayed review, and checkpoint/resumption remain to be observed.

## Learning evidence

Development validation does not assess any learner or establish a certification result. Individual objective status is private; the public templates contain empty defaults for a new learner.
See [REPOSITORY_REVIEW.md](REPOSITORY_REVIEW.md), [SIMULATOR_INTEGRATION.md](SIMULATOR_INTEGRATION.md), and [ROADMAP.md](ROADMAP.md).

## Public package checks

The GitHub workflow runs package, public-file, and Python regression checks without personal records, toolchains, or the sibling simulator. The [first hosted run passed](https://github.com/Adrian-Mihai-Marghidan/terraform_certification_tutor/actions/runs/38006324091) for commit f2be398 on 2026-10-10, Europe/Bucharest, using Ubuntu and Python 3.12. These checks do not exercise Terraform/the provider or prove new-platform simulator runtime support.

A clean export of all 80 staged public files passed package checks, the Git-free artifact/content guard, and all 42 Python tests both normally and under optimization on macOS arm64 with Python 3.12.3. The same export was initialized as a disposable Git repository and passed the workflow's package and indexed-content checks. Workflow YAML, event selection, read-only permissions, and pinned action references were checked locally before the successful hosted run.
Fresh bootstrap with an explicitly selected timezone passed, and rerunning bootstrap on existing maintainer records preserved every record byte-for-byte. Private summaries are retained under private/development/portfolio-sharing; no personal files or local toolchains were copied into the public export.

The native provider-lock helper also executed genuine providers lock and init -lockfile=readonly commands in private copies on macOS arm64. A dry run preserved the learner lock byte-for-byte; explicit publication created a missing lock only in a disposable fixture, followed by an unchanged dry run. These checks do not plan/apply resources or assess a learner. Local summaries are retained under ignored private/development/lock-validation and lock-publication.
