variable "namespace" {
  description = "deploy monitoring services on this namespace"
  type        = string
  default     = "dev"
}


variable "external-url" {
  description = "External url that jupyterhub cluster is accessible"
  type        = string
}


variable "dashboards" {
  description = "Enabled grafana dashboards"
  type        = set(string)
  default = [
    "Main",
  ]
}

variable "node-group" {
  description = "Node key value pair for bound resources"
  type = object({
    key   = string
    value = string
  })
}


variable "overrides" {
  description = "Grafana helm chart overrides"
  type        = list(string)
  default     = []
}
