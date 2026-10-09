variable "environment" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], lower(var.environment))
    error_message = "Choose dev, test, or prod, ignoring letter case."
  }
}

output "normalized_environment" {
  value = lower(var.environment)
}
