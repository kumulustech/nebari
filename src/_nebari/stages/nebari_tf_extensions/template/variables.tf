variable "environment" {
  description = "Kubernetes namespace to create resources within"
  type        = string
}

variable "endpoint" {
  description = "Endpoint for services"
  type        = string
}

variable "tf_extensions" {
  description = "Nebari Terraform Extensions"
  default     = []
}

variable "nebari_config_yaml" {
  description = "Nebari Configuration"
  type        = any
}

variable "helm_extensions" {
  description = "Helm Extensions"
  default     = []
}
