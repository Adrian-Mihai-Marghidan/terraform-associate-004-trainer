# Start here

## Open the projects

Keep `terraform-certification-mentor` and `terraform-azure-simulator` as independently maintained sibling folders.
Obtain the actual compatible simulator implementation using [COMPANION_SIMULATOR.md](docs/COMPANION_SIMULATOR.md). The mentor repository alone does not contain its provider source or binaries. Do not skip this dependency or substitute built-in resources for required Azure lifecycle practice.
Retain the mentor's hidden `.agents` directory.
Setup targets macOS and Linux, including Linux inside WSL2, on amd64 or arm64. Native Windows setup is not supported.
Runtime execution is verified on macOS arm64; Linux/WSL2 and other platforms remain unverified.

## Prepare local practice

Prerequisites: Codex with access to the local workspace, Python 3.9 or newer, a shell such as Bash or Zsh, and network access for the initial toolchain downloads and provider dependency build. Go and Terraform are installed locally by setup; existing global installations need no changes.

For a fresh setup, have the development agent execute these commands separately from the mentor root, the directory containing `AGENTS.md`:

```bash
python3 scripts/check_package.py
python3 scripts/bootstrap_progress.py
python3 scripts/install_local_tools.py
python3 scripts/setup_simulator.py
```

Setup installs isolated Terraform 1.12.2/Go under ignored `.tools/`, builds the sibling provider, and configures a simulator-only mirror.
Global Terraform is unchanged. The learner does not study Go or provider engineering before Terraform.
No Azure credentials/subscription, portal, or server is needed.
For a fresh personal record, add `--timezone` with your IANA timezone to bootstrap, for example `python3 scripts/bootstrap_progress.py --timezone America/New_York`. Without it, the default is Europe/Bucharest. Existing records are preserved; changing an established preference is a separate explicit learning checkpoint.
Before the first learner init, have the development agent verify the [provider lock for your platform](docs/COMPANION_SIMULATOR.md#provider-locks-on-another-machine). Do not delete a lock or state to bypass a checksum failure.

For an existing setup, preserve its tools, private records, state, and simulator storage. Reinstall or rebuild only when a startup check identifies a problem.
In every new terminal, start from the mentor root and run these commands separately:

```bash
source private/simulator-env.sh
terraform version
python3 scripts/check_simulator.py labs/05-simulator-resource-group
```

See [SIMULATOR_INTEGRATION.md](docs/SIMULATOR_INTEGRATION.md) for startup, storage, unsupported behavior, and resumption.
Keep your records and associated simulator storage/state in a separate private backup; Git deliberately ignores them. Each learner uses their own local private records and lab state.
Provider lock files remain eligible for commits. A new clone needs local simulator setup and its own private continuity backup; current maintainer Git status is not part of the course.

## Start tutoring

Open Codex in the mentor root and invoke `$terraform-certification-tutor`.

```text
Read AGENTS.md and use the repo-local terraform-certification-tutor skill.
Recover private progress, handoff, gaps, and reviews without resetting records.
Treat my Terraform knowledge as zero unless learner evidence proves otherwise.
Prepare for Associate 004 using Terraform 1.12 behavior and official references.
Use real Terraform CLI with the required sibling Azure simulator for Azure lifecycle practice.
Built-in resources supplement concepts; never silently replace the simulator.
Summarize verified results and deferred work, then begin lesson 00.1.
Explain desired state/IaC, ask one prediction question, and wait.
When CLI practice begins, check provider/store/lab and teach one command at a time.
Do not run assessed exercises for me or count agent checks as my competence.
Checkpoint actual evidence and the next action after meaningful learning.
```

The first CLI lab is [05-simulator-resource-group](labs/05-simulator-resource-group/README.md), reached in lessons 01.1–01.3 after foundations.
You execute and explain your own exercise; the agent used a separate disposable copy.

## Resume

```text
Use $terraform-certification-tutor.
Recover private handoff/progress/reviews, simulator setup, learner state, and infrastructure storage.
Summarize the last verified learner result and continue the next unfinished lesson.
Preserve pending steps and repeat simulator startup checks before commands.
```

Ask for a checkpoint before stopping. Pending work remains pending.
