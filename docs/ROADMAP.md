# Mentor roadmap

## Implemented and verified

The mentor has an ordered curriculum for all 37 objectives, tutor protocols, assessment rules, continuity records, required simulator setup/startup checks, and a Resource Group learner configuration.
The independent sibling simulator's Resource Group milestone passed using Terraform 1.12.2 on macOS arm64. See [VALIDATION.md](VALIDATION.md).
Five built-in configurations remain supplemental.
The repository review added regression tests, independent agent validation fixtures, and safer installation/startup/storage handling; see [REPOSITORY_REVIEW.md](REPOSITORY_REVIEW.md).

## Learning acceptance

New learners begin lesson 00.1, then follow the curriculum in order. Individual progress lives only in their private records.
Observe learner execution, explanations, troubleshooting, independent variations, delayed review, checkpoint, and resumption.
Development validation does not advance learner status.
Prepare later simulator lesson variants only when needed.

## Unimplemented or separate

Additional Azure types, simulator data sources/import, Azure service fidelity, HCP, and remote backend behavior are unimplemented.
Follow [unsupported-topic guidance](SIMULATOR_INTEGRATION.md).
Simulator development is independently maintained.

## Public reuse

MIT licensing, portfolio/provenance guidance, contribution/privacy instructions, first-setup timezone selection, and package CI support shared use. Publication requires the separately available compatible simulator and actual hosted CI execution; see [PORTFOLIO.md](PORTFOLIO.md).
