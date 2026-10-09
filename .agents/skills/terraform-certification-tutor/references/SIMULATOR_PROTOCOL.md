# Simulator practice protocol

Read repository `docs/SIMULATOR_INTEGRATION.md` and `labs/LAB_COVERAGE.md`.
The default Azure lifecycle environment is the separate sibling `../terraform-azure-simulator`, connected as `terraform.local/learning/azuresim`.

Before practical commands:

1. Check the implementation exists, not just references to it.
2. Recover `private/SIMULATOR_SETUP.json`; verify actual Terraform 1.12.x and provider 0.1.1.
3. Have the learner source `private/simulator-env.sh` in their terminal and run `python3 scripts/check_simulator.py labs/05-simulator-resource-group` from the mentor root.
4. Inspect configuration and state provider identities, the local-only mirror, default workspace, and the actual independent per-lab simulator storage attribute. Existing state/store data must be preserved. This starter contract supports one unaliased provider; prepare separate guarded variants when aliases/modules are taught.
5. Continue the next curriculum step, with prediction, one actual command, observed output, diagnosis, and teach-back.

Use `labs/05-simulator-resource-group` for first Azure lifecycle practice.
Only Resource Groups are currently implemented: create/read/tag-update/delete, name/location replacement, and controlled out-of-band tag changes or deletion.
Explain these as simulated resource operations driven by real Terraform.

Built-in local labs supplement language concepts. Never silently substitute them for the simulator requirement.
For data sources, import, other Azure features, remote locking, secrets features, and HCP Terraform, state unsupported behavior and use a clearly separate local exercise or official-documentation scenario.
Do not claim AzureRM compatibility, remote API fidelity, hosted behavior, or unperformed competence.

The development agent builds and repairs the provider; learning Go is not an advancement gate.
Acceptance checks use `scripts/validate_simulator.py` in a disposable private lab. They do not execute the learner's exercise or update objective mastery.
