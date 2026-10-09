# First local resource

Supplemental built-in exercise. The required default Azure lifecycle lab is [05-simulator-resource-group](../05-simulator-resource-group/README.md).

Lesson 01.1–01.3. Predict each command's effect before running it.
Read the example line by line with the tutor.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform state list
terraform plan
terraform destroy
```

Expected signs: one `terraform_data.example`, a message output after apply, no changes on repeat plan, and resource removal on destroy.
Actual wording and generated IDs must be observed.

Independent variation: change the message, predict the plan, execute, then explain whether Terraform updates or replaces the resource.
Troubleshooting: deliberately refer to a nonexistent resource name in the output, validate, explain the error, and repair it.
Production comparison: a cloud provider would operate on external APIs; this resource only follows a state lifecycle.
