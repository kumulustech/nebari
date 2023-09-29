module "extension" {
  for_each = { for extension in var.tf_extensions : extension.name => extension }

  source = "./modules/nebariextension"

  name             = "nebari-ext-${each.key}"
  namespace        = var.environment
  image            = each.value.image
  urlslug          = each.value.urlslug
  private          = lookup(each.value, "private", false)
  jwt              = lookup(each.value, "jwt", false)
  nebariconfigyaml = lookup(each.value, "nebariconfigyaml", false)
  external-url     = var.endpoint

  envs = lookup(each.value, "envs", [])
}
