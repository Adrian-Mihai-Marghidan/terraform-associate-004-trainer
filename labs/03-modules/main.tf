module "service" {
  source = "./modules/service"

  name        = "api"
  environment = "dev"
}

output "service_details" {
  value = module.service.details
}
