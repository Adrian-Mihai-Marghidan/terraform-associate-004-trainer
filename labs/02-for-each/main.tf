variable "services" {
  description = "Fictional services to practice stable resource keys."
  type = map(object({
    tier = string
  }))
  default = {
    api = {
      tier = "backend"
    }
    web = {
      tier = "frontend"
    }
  }
}

resource "terraform_data" "service" {
  for_each = var.services

  input = {
    name = each.key
    tier = each.value.tier
  }
}

output "service_details" {
  value = {
    for key, instance in terraform_data.service : key => instance.output
  }
}
