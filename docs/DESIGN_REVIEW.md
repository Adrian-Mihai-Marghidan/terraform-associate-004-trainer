# Review of the initial proposal

## Outcome

Corrected requirement: Codex tutor, teaching from zero, Associate 004 first, official references, real Terraform CLI against the required local Azure simulator, and repository continuity. Simulator development is development-agent work; learning Go is not a learner prerequisite.

The mentor is a concrete repository package of instructions, protocols, scripts, and configurations. Its executable Terraform simulator is a separate provider project. Validation scope and learning evidence are recorded separately; a packaged curriculum does not establish completed lessons.

## Corrections

| Finding | Correction | Why it matters |
| --- | --- | --- |
| Domain-level curriculum could leave subobjectives untracked | Map all 37 official IDs to lessons and individual progress records | Coverage becomes inspectable. |
| Long initial diagnostic contradicts learning from zero | Start at 00.1; baseline is small, optional, and not a skip gate | Foundations are taught rather than presumed. |
| General mastery could displace certification | Distinguish core syllabus, optional engineering depth, and practical status | Tests, CI/CD, and provider development do not delay core study. |
| Current docs can show features newer than the exam | Use 1.12.x for examples and record the actual CLI | The learner does not accidentally study newer command semantics as exam facts. |
| Assessment format and scoring were underspecified | Support all published formats; declare practice-only grading/readiness criteria | A generated quiz is not mistaken for an official exam prediction. |
| Memory depended on intended file updates | Define authoritative private records and a non-overwriting bootstrap | Fresh sessions have a concrete resume procedure. |
| Public progress conflicted with private-learning expectations | Keep templates public and personal records ignored, with a private backup requirement | Versioned course material does not expose personal notes. |
| terraform_data could be overinterpreted as cloud simulation | State exactly what each lab can demonstrate | Local lifecycle output cannot prove Azure API, backend, or hosted behavior. |
| 4h could be narrowed to newer features | Cover secrets/Vault together with sensitive, ephemeral, and write-only behavior | Official broad wording and the change summary are both covered. |
| HCP live access could become an unnecessary prerequisite | Teach with documentation and scenarios; label optional actual account work separately | Exam study can continue without falsely claiming hands-on HCP experience. |

## Current validation limits

Package structure, JSON records, script behavior, and skill metadata can be checked here.
In the original package-creation environment, the Terraform CLI and a local VS Code Codex session were unavailable.
This was the original package-creation environment. The current integration now has isolated Terraform 1.12.2 and a verified Resource Group development milestone; see [VALIDATION.md](VALIDATION.md). Learner skill discovery, end-to-end teaching, and checkpoint/resume acceptance remain to be observed.

Only later exercises that are actually created and validated may be reported as implemented.

## Simulator requirement correction

The old project specification excluded a custom provider and marked the simulator optional; AGENTS.md prevented its roadmap integration; curriculum X.2 and lab coverage routed Azure practice to built-in resources. Those statements conflicted with the learner's explicit intended requirement and have been corrected with their authorization.
The mentor now connects to a separate sibling implementation, with a distinct local provider, independent infrastructure storage, startup checks, and genuine disposable Terraform validation.

The subsequent full repository review corrected demonstrated storage, startup, installation, and validation defects; see [REPOSITORY_REVIEW.md](REPOSITORY_REVIEW.md).
