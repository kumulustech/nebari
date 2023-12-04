provider "kubernetes" {
  host                   = aws_eks_cluster.main.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.main.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.main.token
}

data "kubernetes_config_map" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  # Ensure the data source waits for the cluster to be created
  depends_on = [
    aws_eks_cluster.main,
    aws_eks_node_group.main
  ]
}


locals {
  additional_map_roles = [
    {
      rolearn  = "arn:aws:sts::877956244955:assumed-role/AWSReservedSSO_AdministratorAccess_2c9f8c56ed1e3718/*"
      username = "admin:{{SessionName}}"
      groups   = ["system:masters"]
    }
    # You can add more roles here if needed
  ]
}

resource "kubernetes_config_map" "aws_auth" {
  depends_on = [data.kubernetes_config_map.aws_auth]

  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = yamlencode(merge(
      yamldecode(data.kubernetes_config_map.aws_auth.data["mapRoles"]),
      local.additional_map_roles
    ))
  }
}
