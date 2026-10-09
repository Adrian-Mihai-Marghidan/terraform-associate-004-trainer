resource "terraform_data" "example" {
  input = "My first Terraform resource"
}

output "message" {
  value = terraform_data.example.output
}
