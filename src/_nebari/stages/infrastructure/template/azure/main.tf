resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name
  location = var.region
  tags     = var.tags
}


module "registry" {
  source = "./modules/registry"

  name                = "${var.name}${var.environment}"
  location            = var.region
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags
}


module "kubernetes" {
  source = "./modules/kubernetes"

  name                = "${var.name}-${var.environment}"
  environment         = var.environment
  location            = var.region
  resource_group_name = azurerm_resource_group.resource_group.name
  # Azure requires that a new, non-existent Resource Group is used, as otherwise
  # the provisioning of the Kubernetes Service will fail.
  node_resource_group_name = var.node_resource_group_name
  kubernetes_version       = var.kubernetes_version
  tags                     = var.tags

  dynamic "network_profile" {
    for_each = var.network_profile != null ? [var.network_profile] : []
    content {
      network_plugin     = network_profile.value.network_plugin != null ? network_profile.value.network_plugin : null
      network_policy     = network_profile.value.network_policy != null ? network_profile.value.network_policy : null
      service_cidr       = network_profile.value.service_cidr != null ? network_profile.value.service_cidr : null
      dns_service_ip     = network_profile.value.dns_service_ip != null ? network_profile.value.dns_service_ip : null
      docker_bridge_cidr = network_profile.value.docker_bridge_cidr != null ? network_profile.value.docker_bridge_cidr : null
    }
  }

  node_groups = [
    for name, config in var.node_groups : {
      name          = name
      auto_scale    = true
      instance_type = config.instance
      min_size      = config.min_nodes
      max_size      = config.max_nodes
    }
  ]
  vnet_subnet_id          = var.vnet_subnet_id
  private_cluster_enabled = var.private_cluster_enabled
}
