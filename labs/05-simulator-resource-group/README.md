# Simulated Azure Resource Group

Default Azure lifecycle lab for lessons 01.1–01.3, with tag updates and drift used later.
Objectives: 3a–3g and 2d; provider installation supports 2a/2b, and real local drift supports 6d.
The tutor teaches these in curriculum order, one concept and one command at a time.

Terraform Core evaluates this configuration and produces genuine plans and state. The custom provider creates Resource Groups in local JSON storage; Azure is not contacted.

## Prepare

Complete [simulator setup](../../docs/SIMULATOR_INTEGRATION.md) from the mentor root.
In each new terminal, run separately:

```bash
source private/simulator-env.sh
python3 scripts/check_simulator.py labs/05-simulator-resource-group
cd labs/05-simulator-resource-group
```

## First workflow

Predict each command, run it, inspect actual output, and explain what changed.
This list is a reference for several lesson turns, not a request to run it all at once.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform state list
terraform plan
```

Expected signs: provider azuresim 0.1.1 installed from the local mirror; a plan to create one Resource Group; address `azuresim_resource_group.lesson`; no changes on the repeated plan.
These are expectations until the learner runs them.

Inspect the separate simulated infrastructure:

```bash
simctl list --storage "$PWD/.simulator/infrastructure.json"
```

`terraform.tfstate` records Terraform's bindings and last observations.
`.simulator/infrastructure.json` records the objects managed by the simulator.
Never edit Terraform state JSON by hand.

## Later update and drift exercises

For an ordinary desired-state update, edit `environment = "learning"` to `environment = "practice"` in `main.tf`, predict the plan, then run plan and apply separately. Tags update in place.

For a controlled out-of-band change, leave the configuration alone and use:

```bash
simctl set-tags --storage "$PWD/.simulator/infrastructure.json" --name mentor-rg --tags '{"environment":"external"}'
terraform plan
```

Terraform reads the changed storage through the provider and plans to restore configured tags.
Later compare this with `terraform plan -refresh-only`: it proposes recording observed drift in state, without changing the simulated resource. Review plans before applying.

## Cleanup

```bash
terraform destroy
simctl list --storage "$PWD/.simulator/infrastructure.json"
```

The simulated Resource Group should be removed. Terraform state and the empty simulator store/lock may remain on disk.

## Independent practice and troubleshooting

Choose a new name and tag, predict the change, execute it yourself, and explain the result.
A changed name or location requires replacement in this provider.
Try an invalid name containing a slash, observe the diagnostic, and repair it.

## Boundaries

This provider supports only `azuresim_resource_group` with name, location, tags, and a computed ID. Its familiar arguments are a limited AzureRM-style subset. Provider names, source address, IDs, diagnostics, and location validation differ from AzureRM. `features {}`, authentication, other Azure resources, data sources, and import are unsupported.

The dedicated CLI mirror allows only this custom provider. Always run startup checks, and never substitute the real AzureRM provider.
Agent validation uses a dedicated fixture in a disposable private copy; this learner folder has not been applied by the agent.
