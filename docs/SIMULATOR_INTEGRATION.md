# Required simulator integration

The default environment for Azure lifecycle practice is the independent sibling `../terraform-azure-simulator`. The actual HashiCorp Terraform CLI owns evaluation, dependencies, plans, state, refresh, and lifecycle processing. The custom provider owns locally simulated resource operations. Go/provider development belongs to the development agent, never as a learner prerequisite.

## Setup

The sibling must contain actual implementation files (`go.mod`, `internal/provider/provider.go`, `scripts/build.py`). Documentation alone is insufficient. If moved, pass `--simulator-root /absolute/path` to setup.

Obtain the compatible source as described in [COMPANION_SIMULATOR.md](COMPANION_SIMULATOR.md). A mentor clone alone does not supply the simulator.

From the mentor root, run these separately:

```bash
python3 scripts/bootstrap_progress.py
python3 scripts/install_local_tools.py
python3 scripts/setup_simulator.py
source private/simulator-env.sh
python3 scripts/check_simulator.py labs/05-simulator-resource-group
```

The development agent prepares these tools. The learner then studies Terraform, not Go.
The installer downloads isolated Terraform 1.12.2 and Go 1.27.2 from official release sites, verifies SHA256 manifests, and installs under ignored `.tools/`. Global Terraform is unchanged. Initial builds need network access for dependencies; cached local lab operations need no cloud access.
Supported hosts are macOS and Linux/WSL2, amd64/arm64. Only macOS arm64 runtime execution is verified here.

Setup creates `private/SIMULATOR_SETUP.json` with paths/version/hash/platform, `private/simulator-env.sh` with terminal-local PATH/configuration, and `.tools/simulator.tfrc` with an unpacked filesystem mirror allowing only the simulator. There is no direct registry fallback.
No Azure credentials, subscription, portal, server, or background process is needed.

## Startup checks

Source the environment in each new terminal. Run the checker from the mentor root before entering the lab.
It verifies the active 1.12.x CLI, exact mirror configuration, provider and control-tool hashes, exact starter provider pin, configuration/state provider identities, default workspace, and simulator storage access/schema.
The simulator control tool parses actual HCL blocks and evaluates the storage attribute in a restricted context; comments cannot satisfy or invalidate these checks. Terraform itself inspects the provider requirements.
It rejects AzureRM/AzAPI, unexpected or aliased providers, override/JSON files, modules/backends/cloud blocks, named workspaces, storage symlinks, and conflicting Terraform environment variables in this starter lab.
Configuration identities are inspected by Terraform in a temporary configuration-only copy, so a first-run lock file does not require initialization. Existing local state provider identities are checked separately without modifying state.
The provider separately validates its schema and rejects Terraform-state storage paths.

Preserve existing files. Rebuild only when needed. Setup builds and tests in staging, then refuses a changed checksum for an already installed provider version before modifying active tools. Release a new version for changed provider code. Previous setup records/control binaries are backed up under private/development/setup-history; old mirror versions remain installed.
Preserve the old lock/state, verify the new source/binary, generate a lock in a disposable copy, then intentionally reconcile the learner lock. Never delete state or stores to make a command pass. Existing toolchains with a different version/platform are preserved with a diagnostic; the installer never silently replaces them.

From the lab directory use actual `terraform init`, `terraform validate`, `terraform plan`, `terraform apply`, and `terraform destroy`, one explained command at a time.
See [the learner lab](../labs/05-simulator-resource-group/README.md).

## Supported contract

Source: `terraform.local/learning/azuresim`; pinned version: `0.1.1`. This is a locally distributed identity, not a published registry service.
Use `provider "azuresim"` and `azuresim_resource_group`. Never substitute `hashicorp/azurerm`, AzAPI, authentication, or real Azure resources.

Only Resource Groups are implemented. Familiar AzureRM-style body arguments are `name`, `location`, and string-map `tags`; `id` is computed.
Tags update in place; name/location changes require replacement. Names are case-insensitively unique per store.
IDs are deterministic `/subscriptions/local-simulator/resourceGroups/<lowercase-name>` strings.
Locations are lowercase labels, not a verified Azure region catalogue. This limited contract is not full AzureRM compatibility or Azure service fidelity.
No `features {}`, other Azure types, data sources, import, RBAC, policy, authentication, or Azure network behavior is supported.

## Separate storage

Default lab: `labs/05-simulator-resource-group`.

| File | Purpose |
| --- | --- |
| `main.tf` / `versions.tf` | Learner configuration and explicit provider requirements |
| `terraform.tfstate` | Terraform bindings and last recorded observations |
| `.simulator/infrastructure.json` | Provider-managed simulated infrastructure |
| `.simulator/infrastructure.json.lock` | Local storage write lock |
| `.terraform.lock.hcl` | Provider selection and package checksums |

The store uses schema version 1, atomic replacement, file locking, and corruption diagnostics. Only a missing file represents an empty new environment. Existing storage must include its schema/resource map and complete Resource Group fields, including a non-null string-map of tags; malformed storage is rejected and preserved. Its process lock does not demonstrate remote Terraform backend locking.
Inspect with `simctl list`; create controlled drift with `simctl set-tags` or deletion. These leave Terraform state alone. Provider Read exposes external changes or absence during real refresh.
Configuration edits alone are not external drift.

## Resume and backup

Read private handoff, progress, gaps, and due reviews first. Recover setup, learner lab, store path, provider version, and last actual learner command.
Source the terminal environment and repeat startup checks. Preserve Terraform state and infrastructure storage together; changing storage_path can change the environment Terraform observes.
Each learner needs a separate private backup of their own records, state, and storage. Git ignores `private/`, `.tools/`, stores, state, plans, logs, and credential/variable files. A clone does not restore private continuity.
Provider lock files and simulator `go.mod`/`go.sum` remain eligible for commits.

## Unsupported certification topics

| Topic | Explicit alternative |
| --- | --- |
| 4a data sources | Official explanations and a separately verified local-only resource/data-source exercise with its own safe provider mirror |
| 7a import | Official imperative/import-block examples and a separately verified import-capable local resource; simulator import stays unperformed |
| 6b/6c remote locking/backends | Official configurations/concurrency scenarios; live backend behavior needs separate controlled execution |
| 4h sensitive/Vault/ephemeral/write-only | Terraform 1.12 docs and fictional-value exercises with verified provider support |
| 8a–8d HCP Terraform | Current official run/governance/workspace/integration scenarios; account exercises only on request |
| Other Azure behavior | Name the gap; development agent proposes a scoped addition or an explicitly separate exercise |

Never silently replace simulator lifecycle practice with built-in resources.
When practical execution is unsupported or blocked, record it as deferred while clearly distinguishing conceptual study. HCP understanding can be assessed without claiming live HCP execution.

## Validation

```bash
python3 scripts/validate_simulator.py
```

This copies the fixed tests/fixtures/simulator-resource-group configuration into a new private disposable lab, retains actual logs/JSON plans, and destroys its simulated group. Learner edits cannot change the validation fixture. It never runs or modifies learner configuration, state, storage, progress, or lock files.
Generate/reconcile a learner lock separately when installing a new provider version or verifying a new native platform; use the explicit [lock workflow](COMPANION_SIMULATOR.md#provider-locks-on-another-machine). The startup checker covers the actual learner configuration; later alias/module lessons need their own explicit safe startup contracts instead of weakening this starter guard.
See [VALIDATION.md](VALIDATION.md) for the executed milestone, regression checks, and supplemental lab results.
The first sandbox run failed during plugin startup; the approved unsandboxed run passed. Evidence is private; see [VALIDATION.md](VALIDATION.md).

Technical contracts follow [HashiCorp Framework resources](https://developer.hashicorp.com/terraform/plugin/framework/resources) and [Terraform 1.12 filesystem mirrors](https://developer.hashicorp.com/terraform/cli/v1.12.x/config/config-file).
