# Exam objective map

Target: **Associate 004, Terraform 1.12**.
Verified: **2026-10-10, Europe/Bucharest**.
Primary syllabus: [official objectives](https://developer.hashicorp.com/certifications/terraform-associate).
Supporting sources: [content map](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004) and [study path](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-study-004).

The short topic labels below are paraphrases. Preserve the official IDs in progress and questions.

| ID | Topic | First lesson | Primary evidence |
| --- | --- | --- | --- |
| 1a | IaC meaning | 00.1 | concept |
| 1b | IaC benefits | 00.1 | concept |
| 1c | Cross-platform workflows | 00.2 | concept |
| 2a | Provider installation/versioning | 02.1 | cli |
| 2b | Provider responsibility | 02.1 | concept |
| 2c | Multiple provider configurations | 02.2 | cli |
| 2d | State purpose | 01.3 | cli |
| 3a | Workflow sequence | 01.1 | cli |
| 3b | Directory initialization | 01.1 | cli |
| 3c | Configuration validation | 01.1 | cli |
| 3d | Plan interpretation | 01.2 | cli |
| 3e | Change application | 01.2 | cli |
| 3f | Resource removal | 01.3 | cli |
| 3g | Configuration formatting | 01.1 | cli |
| 4a | Resources versus lookups | 04.1 | cli |
| 4b | Attribute references | 04.1 | cli |
| 4c | Inputs and outputs | 03.1 | cli |
| 4d | Collection/object types | 03.2 | cli |
| 4e | Expressions/functions | 03.3 | cli |
| 4f | Dependency ordering | 04.2 | cli |
| 4g | Custom conditions | 04.3 | cli |
| 4h | Secrets and Vault | 07.1 | concept |
| 5a | Module sources | 06.1 | concept |
| 5b | Module scope | 06.1 | cli |
| 5c | Module composition | 06.1 | cli |
| 5d | Module versioning | 06.2 | concept |
| 6a | Local state backend | 05.1 | cli |
| 6b | State concurrency locks | 05.2 | concept |
| 6c | Remote backend configuration | 05.2 | concept |
| 6d | Drift/state reconciliation | 05.3 | cli |
| 7a | Resource importing | 08.1 | cli |
| 7b | State inspection | 08.1 | cli |
| 7c | Diagnostic logging | 08.2 | cli |
| 8a | Hosted run workflow | 09.1 | concept |
| 8b | Team/governance features | 09.2 | concept |
| 8c | Workspace/project organization | 09.1 | concept |
| 8d | Hosted workflow integration | 09.3 | concept |

The source's change summary highlights ephemeral/write-only values under 4h, while the objective row broadly covers secrets and Vault. Cover both; do not narrow 4h to only newer features.

"cli" means a local exercise should establish procedural competence. "concept" allows scenario assessment for exam readiness; any associated live-service exercise has a separate hands-on status.

Check the official target and objective list at course setup and before exam booking. If sources change or disagree materially, record the difference and propose a syllabus update without silently rewriting completed evidence.

No official domain percentages or passing threshold are assumed.

Practical environment: the required local Azure simulator drives Azure lifecycle exercises through the real Terraform CLI. Its limited resource contract does not change these official objectives. Unsupported provider/service topics use explicit separate exercises or official scenarios; see [SIMULATOR_INTEGRATION.md](SIMULATOR_INTEGRATION.md).
