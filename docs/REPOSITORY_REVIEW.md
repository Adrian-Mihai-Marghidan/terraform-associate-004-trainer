# Repository review

Reviewed on 2026-10-10, Europe/Bucharest: all public mentor files, tutor protocols, objective/progress templates, continuity contracts, scripts, six lab configurations, and the independently maintained sibling simulator implementation.

## Corrections

| Finding | Implemented correction |
| --- | --- |
| Existing storage such as `{}` or `null` was mistaken for absent infrastructure and could be overwritten | Simulator 0.1.1 decodes existing files without defaults, validates required schema/resource fields and non-null string tags, and preserves malformed bytes |
| A commented storage expression could satisfy startup checks while the provider used another store | Official HCL parsing checks actual provider blocks and the storage attribute; harmless comments remain valid |
| Named workspaces bypassed the root state-provider check | The starter lab requires the default workspace before inspecting local state |
| Rebuilding overwrote an installed package before reconciling its checksum | Setup builds/tests in staging, rejects changed installed versions, preserves old mirror packages, and backs up prior setup/tools |
| An existing wrong Go executable was reported as the pinned release | The installer verifies both tools' real versions/platforms, preserves mismatches, and stages downloads/installations atomically |
| Agent validation depended on learner names/tags and could modify their lock | A fixed agent fixture now drives simulator regression tests; learner configuration/state/locks are untouched |
| Python optimization disabled semantic checks | Package/runtime validators now raise explicit errors instead of using `assert` |
| Progress templates could disagree with objective lesson mappings | Package checks compare IDs, lessons, exam target, and Terraform version |
| Documentation omitted some syllabus details and wrote the handoff too early | Curriculum coverage, unscored baseline objective IDs, prerequisites, and handoff-last checkpoint ordering are explicit |

## Validation

See [VALIDATION.md](VALIDATION.md) for executed commands, resource behavior, platform limits, and evidence locations.
Development commands are reproducible from the mentor root:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_package.py
python3 scripts/validate_simulator.py
python3 scripts/validate_local_labs.py
```

Runtime validation uses ignored private copies, separate from learner exercises. These results do not advance learner understanding or practical competence.

## Git and continuity

Private records, toolchains, simulator databases, state, saved plans, logs, environment files, and credential key files are ignored; provider lock files remain versionable.
The sibling simulator remains independently maintained outside this repository. Each learner needs their own private backup; a clone contains course material and scripts, not personal continuity or runtime infrastructure. Current maintainer Git status belongs in the private handoff.

## Further improvements

Prepare guarded simulator aliases/modules and later language exercises when their lessons are reached. Import, data sources, remote backend locking, HCP functionality, and other Azure resource types remain explicit separate work.
Verify Linux/WSL2 and other platforms before claiming runtime support there. Observe a real learner checkpoint/resume cycle before declaring that acceptance criterion complete.

## Public portfolio adaptation

Public material is generalized for other learners, with MIT licensing, companion acquisition/version guidance, provenance and CV claim boundaries, contribution/privacy instructions, a public-file guard, configurable first-setup timezone, and package CI. See [PORTFOLIO.md](PORTFOLIO.md). Hosted CI and publication are separate checks; neither is claimed successful merely because their files exist.
