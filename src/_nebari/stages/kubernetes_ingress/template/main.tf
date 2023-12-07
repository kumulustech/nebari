module "kubernetes-ingress" {
  source = "./modules/kubernetes/ingress"

  namespace = var.environment

  node-group = var.node_groups.general

  traefik-image = var.traefik-image

  certificate-service       = var.certificate-service
  acme-email                = var.acme-email
  acme-server               = var.acme-server
  certificate-secret-name   = var.certificate-secret-name
  load-balancer-annotations = var.load-balancer-annotations
  load-balancer-ip          = var.load-balancer-ip
  additional-arguments      = var.additional-arguments
}

data "aws_route53_zone" "existing" {
  name = "pacioos.dev"
}

resource "aws_route53_record" "test_pacioos_dev_cname" {
  zone_id = data.aws_route53_zone.existing.zone_id
  name    = "test.pacioos.dev"
  type    = "CNAME"
  ttl     = "60"
  records = [module.kubernetes-ingress.endpoint.hostname]
}
