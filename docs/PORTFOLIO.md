# Portfolio and shared use

The primary outcome is learning Terraform from zero toward Associate 004. Public portfolio value and reuse by others are secondary goals; development and publication tasks are not learner advancement gates.

Maintainer account: [Adrian-Mihai-Marghidan](https://github.com/Adrian-Mihai-Marghidan).
Public repository locations and the required companion are documented in [COMPANION_SIMULATOR.md](COMPANION_SIMULATOR.md).

## What a reviewer can inspect

| Design choice | Evidence in source |
| --- | --- |
| Small, ordered teaching steps | AGENTS.md, the tutor skill/protocols, and curriculum mapping |
| Exam understanding separate from execution | Public progress templates and assessment rules; actual learner evidence remains private |
| Real Terraform with local resource operations | Explicit custom source/version, local-only mirror, and the independently maintained simulator |
| Meaningful drift | Terraform state and simulator storage are separate; disposable validation changes storage out of band |
| Safe maintenance | Staged installation, immutable installed package checks, strict simulator storage diagnostics, and regression tests |
| Reproducible development checks | Public Python tests, package checks, artifact guard, fixed fixtures, and local lifecycle validators |
| Session continuity | Non-overwriting personal bootstrap and handoff protocol, with an explicit private backup requirement |

See [README.md](../README.md) for the architecture and [VALIDATION.md](VALIDATION.md) for executed test scope. Public CI checks the mentor package layer. Full simulator runtime requires the separately obtained provider and local toolchain; no green package check implies that integration passed on another platform.

## Provenance and claims

The project was developed through collaboration with Codex: the maintainer specified the learning requirements and directs its maintenance; AI assistance produced and reviewed implementation and documentation. Public execution summaries describe synthetic development checks, not personally assessed learner skills.

A suitable project description is:

> Created and maintained a Codex-assisted Terraform certification study project with an objective-mapped curriculum, private progress tracking, and real CLI practice against an independent local Azure simulator.

Use that description only when you can explain and maintain the parts you present. Describe the provider as a separate related project. Do not imply that local Resource Group exercises prove real Azure provisioning, complete AzureRM compatibility, live HCP/remote backend experience, production operation, or an earned certification.
Include independent learning achievements only when supported by your own verified execution and assessment. Public portfolio updates can be curated summaries; personal records, raw terminal histories, state, plans, and assessments stay private.

## Publication preparation

1. Confirm the mentor source is available in the public terraform_certification_tutor repository and publish the simulator separately with a compatible source/release identity. The simulator endpoint was not publicly accessible during the 2026-10-10 unauthenticated check; complete setup requires both source projects.
2. Include the owner-selected MIT license for original project source and preserve upstream terms. GitHub's [licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) explains why the source repository needs explicit reuse terms.
3. Run package/tests/public-file checks from a clean checkout or source export. Review staged contents and the Git author identity before creating public history.
4. Run the full simulator milestone against the exact source/version being published. Preserve a public summary of behavior/platform; retain raw records locally. Verify package locks separately for additional platforms.
5. Configure the repository's issue/private reporting channels, run the included GitHub workflow, and record its actual result before adding a CI-success badge.

This preparation does not create repositories, publish code, change Git identity, or upload private files. Those actions need a separate publishing instruction.
