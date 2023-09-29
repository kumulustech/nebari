variable "monitoring-enabled" {
  description = "Prometheus and Grafana monitoring enabled"
  type        = bool
}

module "monitoring" {
  count = var.monitoring-enabled ? 1 : 0

  source               = "./modules/kubernetes/services/monitoring"
  namespace            = var.environment
  external-url         = var.endpoint
  node-group = var.node_groups.general
}
