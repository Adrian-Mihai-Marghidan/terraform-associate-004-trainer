variable "environment" {
  description = "A fictional environment label for a local learning resource."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Choose dev, test, or prod."
  }
}

locals {
  label = "mentor-${var.environment}"
}

resource "terraform_data" "environment" {
  input = local.label
}

output "label" {
  value = terraform_data.environment.output
}
