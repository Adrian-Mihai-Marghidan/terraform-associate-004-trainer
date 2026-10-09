# Lab coverage and boundaries

The required default Azure lifecycle lab is `05-simulator-resource-group`, using real Terraform 1.12.x and the distinct local azuresim provider.
The five original built-in configurations are supplemental. Each root has independent Terraform state; simulator roots also have separate infrastructure JSON.

| Folder | Lesson | Demonstrates | Does not establish |
| --- | --- | --- | --- |
| 05-simulator-resource-group | 01.1–01.3; later 02.1/05.3 | Provider installation, real CLI/state lifecycle, persistent simulated groups, tag update, external storage drift | Azure APIs, full AzureRM compatibility, data sources/import, remote locking, HCP |
| 00-first-run | Supplement to 01.1–01.3 | Built-in value lifecycle | Required Azure practice or external object drift |
| 01-variables | Supplement to 03.1/04.3 | Inputs, locals, outputs, validation | Provider secrets or cloud connectivity |
| 02-for-each | Supplement to 03.2–03.3 | Collections, stable keys, addresses | Real Azure replacement semantics |
| 03-modules | Supplement to 06.1 | Child scope and composition | Registry/Git resolution |
| 04-terraform-test | X.1 | Optional plan-only assertions/expected failure | Cloud integration or exam mastery |

The Resource Group integration and all five supplemental configurations have current agent runtime validation here; see [VALIDATION.md](../docs/VALIDATION.md).
Follow curriculum order; listed capabilities do not imply completed lessons.

## Later exercises

- Provider aliases, repetition, dependencies, and modules: prepare Resource Group variants; built-in examples supplement concepts.
- Resource references: use simulator groups. Data sources remain unsupported; use an explicit separate verified local-only exercise and its own safe provider setup.
- Drift: change actual infrastructure with simctl while preserving configuration/state, then refresh.
- Import: unimplemented in azuresim; verify a separate resource's import support or record conceptual-only coverage.
- Remote locking/backends: documented scenarios first; the simulator file lock does not prove remote Terraform locking.
- Secrets: fictional values and actual 1.12/provider support; simulator secret-specific features are unimplemented.
- HCP: current official documentation/scenarios; live account work only on request.

Read [SIMULATOR_INTEGRATION.md](../docs/SIMULATOR_INTEGRATION.md) before practice.
Do not use mocks as evidence of real APIs/backends or configuration edits as evidence of external drift.
