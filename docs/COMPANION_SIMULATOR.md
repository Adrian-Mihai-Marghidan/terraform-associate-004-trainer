# Obtain the required simulator

The mentor connects to a separate implementation, not a simulator specification or scripted command imitation. Keep both source projects independently maintained.

## Repository locations

Account supplied by the maintainer: [Adrian-Mihai-Marghidan](https://github.com/Adrian-Mihai-Marghidan).

| Project | Repository location |
| --- | --- |
| Mentor | https://github.com/Adrian-Mihai-Marghidan/terraform-associate-004-trainer |
| Required simulator | https://github.com/Adrian-Mihai-Marghidan/terraform-azure-simulator |

Both source projects are public. The simulator's compatible [v0.1.1 tag](https://github.com/Adrian-Mihai-Marghidan/terraform-azure-simulator/tree/v0.1.1) was published and verified from a fresh clone on 2026-10-10. Its source is built locally; no provider registry entry or downloadable binary release is provided. Do not run an unrelated provider or silently omit simulator practice.

Clone both projects under a directory you choose:

```bash
git clone https://github.com/Adrian-Mihai-Marghidan/terraform-associate-004-trainer.git terraform-certification-mentor
git clone --branch v0.1.1 https://github.com/Adrian-Mihai-Marghidan/terraform-azure-simulator.git
cd terraform-certification-mentor
```

Use the v0.1.1 source tag identified as compatible below. The clone command checks out that tag in detached HEAD mode, which is appropriate for reproducible setup. Avoid assuming the latest development branch remains compatible with a pinned mentor version.

## Compatibility

| Component | Current contract |
| --- | --- |
| Terraform CLI | 1.12.2 isolated by mentor setup |
| Provider source | terraform.local/learning/azuresim |
| Provider version | 0.1.1 |
| Compatible source tag | v0.1.1 (commit 829bba6) |
| Supported resource | azuresim_resource_group only |
| Source implementation | go.mod/go.sum, internal/provider/provider.go, internal/store, internal/preflight, cmd/simctl, scripts/build.py |
| Distribution | Locally built filesystem mirror; no public provider registry or binary release is claimed |
| Source license | MIT in each independent source project; upstream dependency terms remain separate |
| Runtime evidence | macOS arm64 passed; Linux/WSL2 and other platforms remain unverified |

Run [the setup commands](../START_HERE.md) from the mentor root. A moved simulator can be supplied with `python3 scripts/setup_simulator.py --simulator-root /absolute/path/to/terraform-azure-simulator`.
The development agent handles Go builds and compatibility; learners study Terraform. No Azure subscription, authentication, portal, or daemon is required.

## Provider locks on another machine

The committed starter lock records the verified macOS arm64 package. A local provider build for another platform can require an additional checksum, and toolchain changes can change package bytes. The lock is part of the trust decision; do not delete it or ignore a mismatch to make init pass.

Have the development agent inspect the source/version and setup hashes, then generate/verify a native-platform lock in a disposable configuration using the local mirror. The maintainer helper performs this check without applying resources:

```bash
source private/simulator-env.sh
python3 scripts/reconcile_simulator_lock.py labs/05-simulator-resource-group
```

The default only reports the result. After reviewing it, use `--write` to retain a private backup and deliberately reconcile the learner lock. Configuration, state, and infrastructure remain untouched. A changed same-version installed provider is still rejected by setup; lock reconciliation does not authorize overwriting an immutable package.

This follows HashiCorp's [Terraform 1.12 mirror-based provider locking](https://developer.hashicorp.com/terraform/cli/v1.12.x/commands/providers/lock). The verified native check does not establish Linux or other-platform runtime success.
