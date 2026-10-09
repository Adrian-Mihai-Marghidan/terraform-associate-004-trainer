provider "azuresim" {
  storage_path = "${abspath(path.root)}/.simulator/infrastructure.json"
}

resource "azuresim_resource_group" "lesson" {
  name     = "mentor-rg"
  location = "eastus"

  tags = {
    environment = "learning"
  }
}

output "resource_group" {
  value = {
    id       = azuresim_resource_group.lesson.id
    name     = azuresim_resource_group.lesson.name
    location = azuresim_resource_group.lesson.location
    tags     = azuresim_resource_group.lesson.tags
  }
}
