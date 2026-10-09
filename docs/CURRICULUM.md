# Curriculum

Certification comes first. Complete the ordered foundations without assuming professional Terraform competence. Lessons are small units that may span several turns.

| Lesson | Topic | Objectives | Demonstration or assessment |
| --- | --- | --- | --- |
| 00.1 | Desired state and IaC | 1a, 1b | Describe the intended result of a manual Azure change and a declarative configuration. Predict why a plan is useful. |
| 00.2 | Terraform Core and providers | 1c | Explain which component constructs a plan and which component talks to a service. Define multi-cloud, hybrid cloud, and service-agnostic workflows with one small example at a time; compare Azure with another provider without requiring Azure knowledge. |
| 01.1 | Files, init, fmt, validate | 3a, 3b, 3c, 3g | Inspect the simulator Resource Group configuration in labs/05-simulator-resource-group. Check setup, then run each command separately and explain what changed on disk. |
| 01.2 | Plan, apply, repeat | 3d, 3e | Predict Resource Group creation, apply to separate simulator storage, then show an unchanged plan. Explain a saved plan before using it. |
| 01.3 | State and destroy | 2d, 3f | Inspect a resource address, identify state purpose, destroy the simulated Resource Group, and explain what remains on disk. |
| 02.1 | Provider requirements and locks | 2a, 2b | Inspect actual simulator mirror installation and lock selection; compare Core constraints, provider constraints, and provider selections. Explain how registry distribution differs. |
| 02.2 | Multiple providers and aliases | 2c | Prepare simulator aliases with separate stores and a built-in provider example. Explain multiple provider configurations and why configuration differs from installation; no real Azure provider. |
| 03.1 | Variables, locals, outputs | 4c | Add a Resource Group tag input and local value in an isolated simulator exercise. Use the built-in variables lab as a supplement; explain scope, defaults, overrides, and outputs. |
| 03.2 | Types and collections | 4d | Construct a list, set, map, and object. Explain when an object attribute and map key differ. |
| 03.3 | Expressions and repetition | 4e | Use console, functions, conditionals, count and for_each with simulator Resource Groups; the bundled built-in for_each lab is supplemental. Predict address changes. |
| 04.1 | Resources, data, references | 4a, 4b | Use Resource Group references. Simulator data sources are unsupported; prepare an explicitly separate verified local_file resource/data-source exercise with its own safe provider setup. |
| 04.2 | Dependencies and lifecycle | 4f | Prepare Resource Group references, justify an explicit dependency, and demonstrate name replacement. Use distinct names for create_before_destroy; simulator groups do not model Azure child containment. |
| 04.3 | Custom conditions | 4g | Trigger a variable validation failure. Explain preconditions, postconditions, and checks, including blocking versus warning behavior. |
| 05.1 | Local state and backends | 6a | Inspect simulator lab state with CLI commands. Distinguish configuration, Terraform state, and persistent simulated infrastructure. |
| 05.2 | Locking and remote storage | 6b, 6c | Read a remote backend configuration and solve a concurrency scenario; explain migration, credentials, and backend-specific locking support. |
| 05.3 | Drift and refactoring | 6d | Modify Resource Group tags in simulator storage with simctl, leaving Terraform state/configuration unchanged. Predict normal and refresh-only plans. Prepare separate isolated exercises for moved and removed blocks; distinguish changing a resource address, relinquishing management with destroy = false, and destroying infrastructure. |
| 06.1 | Modules and scope | 5a, 5b, 5c | Prepare a local module around a simulated Resource Group with explicit provider passing. The bundled built-in module is supplemental. Explain scope and local/Git/registry sources. |
| 06.2 | Versioned module dependencies | 5d | Contrast registry version selection with a Git ref and a local path. Explain why the provider lock file does not pin modules. |
| 07.1 | Sensitive, ephemeral, write-only, Vault | 4h | With fictional values, explain redaction versus persistence, legal ephemeral contexts, provider-specific write-only support, and why retrieving secrets from Vault alone does not guarantee absence from state. |
| 08.1 | Import and state inspection | 7a, 7b | Inspect actual simulator lab state. Simulator import is unimplemented; explain import using official docs and prepare a separately verified import-capable local provider exercise. |
| 08.2 | Troubleshooting and logs | 7c | Reproduce a harmless local error, investigate it, and enable scoped diagnostic logging without recording real credentials. |
| 09.1 | HCP runs and workspace model | 8a, 8c | Follow a documentation-grounded run scenario; distinguish HCP workspaces and projects from CLI workspace state selection. Introduce project organization, variable sets, and run triggers one scenario at a time. |
| 09.2 | Collaboration and governance | 8b | Solve separate scenarios involving teams, permissions, private modules, policy checks, dynamic provider credentials, and health assessments including drift detection. Verify current feature availability before quoting it; conceptual scenarios do not establish live HCP execution. |
| 09.3 | HCP CLI and VCS integration | 8d | Interpret cloud integration configuration and compare CLI-driven and VCS-driven workflows; an actual account exercise is optional. |
| 10.1 | Targeted revision | all | Review the weakest assessed objectives using new examples and delayed retrieval; exclude repeated questions from unseen-question scores. |
| 11.1 | Timed practice and readiness | all | Run an original 60-minute practice assessment and produce a per-domain review, with no claimed equivalence to official scoring. |
| X.1 | Optional Terraform testing | extension | Use the optional plan-only test lab after learning the relevant language features. This extension is not an exam prerequisite. |
| X.2 | Optional engineering practice | extension | CI/CD, advanced Azure deployments, and learning provider engineering remain separate from the certification path. Simulator implementation is development-agent work supporting required practice. |

## Advancement

For a procedural topic, pair a learner-executed task with an explanation and an independently corrected harmless failure. Do not turn optional engineering depth into a mandatory gate.
For a conceptual topic, require an accurate explanation and a fresh scenario.
If the learner requests exam-focused advancement while hands-on work is deferred, preserve the pending practical status and schedule it for later.

After each core topic, use two to five original questions and one short teach-back.
At the end of each domain, review the objective map for omissions.
Delayed review starts with small prompts; it does not force an arbitrary daily schedule.

## Lab implementation

Six starter configurations are present: the required simulator Resource Group lab and five supplemental built-in configurations. Their code is an example, not evidence that the learner wrote a solution.
Ask for a small independent variation before recording procedural competence.
Prepare later lab files only when their lesson is reached, following [LAB_COVERAGE.md](../labs/LAB_COVERAGE.md).

Coverage follows the [official Associate 004 content map](https://developer.hashicorp.com/terraform/tutorials/certification-004/associate-review-004), including its state-refactoring and HCP topics. Use [Terraform 1.12 removed-block behavior](https://developer.hashicorp.com/terraform/language/v1.12.x/block/removed) for the distinction between leaving infrastructure in place and destroying it. These lesson descriptions identify planned study; they do not claim the exercises or learner assessments have been completed.
