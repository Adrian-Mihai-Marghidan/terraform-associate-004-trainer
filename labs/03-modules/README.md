# Local module scope

Supplemental language exercise; the tutor prepares a Resource Group module variant for required Azure lifecycle practice.

Lesson 06.1. Execute in this root directory, not its child folder.

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
terraform apply
terraform output
terraform state list
terraform destroy
```

Expect a child resource address beginning with `module.service`.
Independently add a second module instance with different inputs; predict its output and address.
Explain why the child does not automatically inherit root variable values.
Production comparison: a local path does not demonstrate registry module version constraints.
