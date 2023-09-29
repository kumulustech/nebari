output "service_urls" {
  description = "service urls for configured services"
  value = {
    monitoring = {
      url        = var.monitoring-enabled ? "https://${var.endpoint}/monitoring/" : null
      health_url = var.monitoring-enabled ? "https://${var.endpoint}/monitoring/api/health" : null
    }
  }
}
