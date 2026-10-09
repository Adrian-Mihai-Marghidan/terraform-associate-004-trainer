# Inputs, locals, outputs, and validation

Supplemental language exercise; Resource Group lifecycle practice uses [the simulator](../05-simulator-resource-group/README.md).

Lesson 03.1 and 04.3. Work from this directory.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform output
terraform plan -var='environment=test'
terraform plan -var='environment=invalid'
terraform destroy
```

The valid change should propose a changed label. The invalid value should produce a custom validation diagnostic.
Predict both before execution. The destroy command removes only this lab's local resource.

Independent variation: add another valid environment and explain the validation condition.
Explain why a variable declaration differs from supplying its value.
Production comparison: real environment isolation needs deliberate backend and access design; a string label alone does not isolate infrastructure.
