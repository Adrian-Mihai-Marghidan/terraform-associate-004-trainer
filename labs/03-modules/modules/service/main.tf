variable "name" {
  type = string
}

variable "environment" {
  type = string
}

resource "terraform_data" "service" {
  input = {
    name        = var.name
    environment = var.environment
  }
}

output "details" {
  value = terraform_data.service.output
}
