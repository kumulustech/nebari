data "aws_availability_zones" "awszones" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

# ==================== ACCOUNTING ======================
module "accounting" {
  source = "./modules/accounting"

  project     = var.name
  environment = var.environment

  tags = local.additional_tags
}


# ======================= NETWORK ======================
# module "network" {
#   source = "./modules/network"

#   name = local.cluster_name

#   tags = local.additional_tags

#   vpc_tags = {
#     "kubernetes.io/cluster/${local.cluster_name}" = "shared"
#   }

#   subnet_tags = {
#     "kubernetes.io/cluster/${local.cluster_name}" = "shared"
#   }

#   security_group_tags = {
#     "kubernetes.io/cluster/${local.cluster_name}" = "owned"
#   }

#   vpc_cidr_block         = var.vpc_cidr_block
#   aws_availability_zones = length(var.availability_zones) >= 2 ? var.availability_zones : slice(sort(data.aws_availability_zones.awszones.names), 0, 2)
# }

locals {
  vpc_cidr_newbits   = 2
  availability_zones = length(var.availability_zones) >= 2 ? var.availability_zones : slice(sort(data.aws_availability_zones.awszones.names), 0, 2)
}

module "network" {
  source = "terraform-aws-modules/vpc/aws"
  # version = "4.0.2"
  version = "3.19.0"

  name = local.cluster_name
  tags = local.additional_tags
  vpc_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  }
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  }
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
  }
  default_security_group_tags = {
    "kubernetes.io/cluster/${local.cluster_name}" = "owned"
  }

  cidr = var.vpc_cidr_block
  azs  = local.availability_zones

  public_subnets                   = [for i in range(length(local.availability_zones)) : cidrsubnet(var.vpc_cidr_block, local.vpc_cidr_newbits, i)]
  default_vpc_enable_dns_hostnames = true
  default_vpc_enable_dns_support   = true
  enable_dns_hostnames             = true
  enable_dns_support               = true
  map_public_ip_on_launch          = true

  default_security_group_name = local.cluster_name
  default_security_group_egress = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  default_security_group_ingress = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = var.vpc_cidr_block
    }
  ]

  # seems like the below will cause problems, but it was set in the old network module
  lifecycle {
    ignore_changes = [
      azs
    ]
  }
}

# ==================== REGISTRIES =====================
module "registry-jupyterlab" {
  source = "./modules/registry"

  name = "${local.cluster_name}-jupyterlab"
  tags = local.additional_tags
}


# ====================== EFS =========================
module "efs" {
  source = "./modules/efs"

  name = "${local.cluster_name}-jupyterhub-shared"
  tags = local.additional_tags

  efs_subnets = module.network.public_subnets
  # module.network.subnet_ids
  efs_security_groups = [module.network.default_security_group_id]
  # [module.network.security_group_id]
}


# ==================== KUBERNETES =====================
module "kubernetes" {
  source = "./modules/kubernetes"

  name               = local.cluster_name
  tags               = local.additional_tags
  region             = var.region
  kubernetes_version = var.kubernetes_version

  cluster_subnets         = module.network.public_subnets
  cluster_security_groups = [module.network.default_security_group_id]

  node_group_additional_policies = [
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  ]

  node_groups = var.node_groups

  depends_on = [
    module.network
  ]
}
