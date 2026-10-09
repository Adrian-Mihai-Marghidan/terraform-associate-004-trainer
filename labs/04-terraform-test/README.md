# Optional plan-only tests

Extension X.1. This is not a certification prerequisite.
The fixture has no managed resources, providers to download, or cloud access.

```bash
terraform init
terraform fmt -check
terraform validate
terraform test
```

The first run should validate lowercase normalization. The second should accept the declared expected custom-validation failure.
These are expected signs, not recorded successful output.

Independent variation: introduce a deliberate bug in normalization, run the test, interpret the failure, and repair it.
Explain why `command = plan` matters. Terraform tests default to apply when not explicitly overridden.
Production comparison: unit-style assertions do not prove a real cloud integration.
