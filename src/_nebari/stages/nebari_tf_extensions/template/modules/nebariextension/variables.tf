variable "namespace" {
  description = "Namespace to deploy into"
  type        = string
}

variable "name" {
  description = "Name of extension"
  type        = string
}

variable "external-url" {
  description = "URL of the Nebari"
  type        = string
}

variable "image" {
  description = "Docker image for extension"
  type        = string
}

variable "urlslug" {
  description = "Slug for URL"
  type        = string
}

variable "private" {
  description = "Protect behind login page"
  type        = bool
  default     = true
}

variable "jwt" {
  description = "Create secret and cookie name for JWT, set as env vars"
  type        = bool
  default     = false
}

variable "nebariconfigyaml" {
  description = "Mount nebari-config.yaml from configmap"
  type        = bool
  default     = false
}

variable "envs" {
  description = "List of env var objects"
  type        = list(map(any))
  default     = []
}
