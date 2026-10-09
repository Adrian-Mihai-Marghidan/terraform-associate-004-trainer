# for_each and stable keys

Supplemental language exercise; Azure lifecycle repetition uses Resource Group simulator variants prepared by the tutor.

Lesson 03.2–03.3.

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
terraform state list
terraform destroy
```

Expected addresses include `terraform_data.service["api"]` and `terraform_data.service["web"]`.
Independently remove a service, predict the plan, and then verify your prediction.
Compare stable keys with count indexes. Explain why a renamed key can lead to a different resource address.
Production comparison: actual provider schemas decide whether changed attributes update or replace external resources.
