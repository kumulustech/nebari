# ===================== VARIABLES ====================
variable "dask-worker-image" {
  description = "Dask worker image"
  type = object({
    name = string
    tag  = string
  })
}

variable "dask-gateway-profiles" {
  description = "Dask Gateway profiles to expose to user"
  default     = []
}

variable "dask-extra-images" {
  description = "Extra images to pull for Dask Gateway cluster handler"
  default     = {}
}

variable "dask-extra-worker-mounts" {
  description = "Extra mounts to add to Dask Gateway worker pods"
  type        = any
}

variable "dask-init-container-cmd" {
  description = "Command to run in init container"
  type        = bool
}

variable "dask-additional-config" {
  description = "Additional configuration to add to Dask Gateway cluster"
  type = object({
    idle_timeout      = number
    image_pull_policy = string
    environment       = map(string)
  })
}

# =================== RESOURCES =====================
module "dask-gateway" {
  source = "./modules/kubernetes/services/dask-gateway"

  namespace            = var.environment
  jupyterhub_api_token = module.jupyterhub.services.dask-gateway.api_token
  jupyterhub_api_url   = "${module.jupyterhub.internal_jupyterhub_url}/hub/api"

  external-url = var.endpoint

  cluster-image                           = var.dask-worker-image
  cluster-additional-fields-configuration = var.dask-additional-config

  general-node-group = var.node_groups.general
  worker-node-group  = var.node_groups.worker

  # needs to match name in module.jupyterhub.extra-mounts
  dask-etc-configmap-name = "dask-etc"

  # environments
  conda-store-pvc               = module.conda-store-nfs-mount.persistent_volume_claim.name
  conda-store-mount             = "/home/conda"
  default-conda-store-namespace = var.conda-store-default-namespace

  # profiles
  profiles            = var.dask-gateway-profiles
  extra-worker-images = var.dask-extra-images
  init-container-cmd  = var.dask-init-container-cmd
  extra-worker-mounts = var.dask-extra-worker-mounts

}
