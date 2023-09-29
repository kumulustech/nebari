locals {
  middlewares = (var.private) ? ([{
    name      = "traefik-forward-auth"
    namespace = var.namespace
  }]) : ([])
}
