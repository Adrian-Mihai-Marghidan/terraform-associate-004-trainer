terraform {
  required_version = "~> 1.12.0"

  required_providers {
    azuresim = {
      source  = "terraform.local/learning/azuresim"
      version = "= 0.1.1"
    }
  }
}
