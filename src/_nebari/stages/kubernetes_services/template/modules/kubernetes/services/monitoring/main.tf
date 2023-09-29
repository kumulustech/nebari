resource "helm_release" "prometheus-grafana" {
  name       = "nebari"
  namespace  = var.namespace
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "30.1.0"

  values = concat([
    file("${path.module}/values.yaml"),
    # https://github.com/prometheus-community/helm-charts/blob/kube-prometheus-stack-30.1.0/charts/kube-prometheus-stack/values.yaml
    jsonencode({
      alertmanager = {
        alertmanagerSpec = {
          nodeSelector : {
            "${var.node-group.key}" = var.node-group.value
          }
        }
      }

      prometheusOperator = {
        nodeSelector = {
          "${var.node-group.key}" = var.node-group.value
        }

        admissionWebhooks = {
          patch = {
            nodeSelector = {
              "${var.node-group.key}" = var.node-group.value
            }
          }
        }
      }

      kube-state-metrics = {
        # kube-state-metrics does not collect pod labels by default.
        # This tells kube-state-metrics to collect app and component labels which are used by the jupyterhub grafana dashboards.
        metricLabelsAllowlist = ["pods=[app,component,hub.jupyter.org/username,app.kubernetes.io/component,gateway.dask.org/cluster]", "nodes=[*]"] # ["pods=[*]"] would collect all pod labels, but is not recommended.
        nodeSelector = {
          "${var.node-group.key}" = var.node-group.value
        }
      }

      prometheus = {
        prometheusSpec = {
          nodeSelector = {
            "${var.node-group.key}" = var.node-group.value
          }
          additionalScrapeConfigs = [
            {
              "job_name"     = "Kubernetes Services"
              "honor_labels" = true
              "kubernetes_sd_configs" = [{
                "role" = "endpoints"
              }]

              "relabel_configs" = [
                {
                  "action" = "keep"

                  "regex" = true

                  "source_labels" = ["__meta_kubernetes_service_annotation_prometheus_io_scrape"]
                },
                {
                  "action" = "drop"

                  "regex" = true

                  "source_labels" = ["__meta_kubernetes_service_annotation_prometheus_io_scrape_slow"]
                },
                {
                  "action" = "replace"

                  "regex" = "(https?)"

                  "source_labels" = ["__meta_kubernetes_service_annotation_prometheus_io_scheme"]

                  "target_label" = "__scheme__"
                },
                {
                  "action" = "replace"

                  "regex" = "(.+)"

                  "source_labels" = ["__meta_kubernetes_service_annotation_prometheus_io_path"]

                  "target_label" = "__metrics_path__"
                },
                {
                  "action" = "replace"

                  "regex" = "(.+?)(?::\\d+)?;(\\d+)"

                  "replacement" = "$1:$2"

                  "source_labels" = ["__address__", "__meta_kubernetes_service_annotation_prometheus_io_port"]

                  "target_label" = "__address__"
                },
                {
                  "action" = "labelmap"

                  "regex" = "__meta_kubernetes_service_annotation_prometheus_io_param_(.+)"

                  "replacement" = "__param_$1"
                },
                {
                  "action" = "labelmap"

                  "regex" = "__meta_kubernetes_service_label_(.+)"
                },
                {
                  "action" = "replace"

                  "source_labels" = ["__meta_kubernetes_namespace"]

                  "target_label" = "namespace"
                },
                {
                  "action" = "replace"

                  "source_labels" = ["__meta_kubernetes_service_name"]

                  "target_label" = "service"
                },
                {
                  "action" = "replace"

                  "source_labels" = ["__meta_kubernetes_pod_node_name"]

                  "target_label" = "node"
                }
              ]
            }
          ]
        }
      }

      # https://github.com/grafana/helm-charts/blob/main/charts/grafana/values.yaml
      grafana = {
        nodeSelector = {
          "${var.node-group.key}" = var.node-group.value
        }

        sidecar = {
          dashboards = {
            annotations = {
              "dashboard/subdirectory" = "Supplementary"
            }
            provider = {
              foldersFromFilesStructure : true
            }
            # If specified, the sidecar will look for annotation with this name to create folder and put graph here.
            # You can use this parameter together with `provider.foldersFromFilesStructure`to annotate configmaps and create folder structure.
            folderAnnotation : "dashboard/subdirectory"
          }
        }

        "grafana.ini" : {
          server = {
            protocol            = "http"
            domain              = var.external-url
            root_url            = "https://%(domain)s/monitoring"
            serve_from_sub_path = "true"
          }
        }
      }
    })
  ], var.overrides)
}


resource "kubernetes_config_map" "dashboard" {
  for_each = var.dashboards
  metadata {
    name      = "nebari-grafana-dashboards-${lower(each.value)}"
    namespace = var.namespace
    labels = {
      # grafana_dashboard label needed for grafana to pick it up
      # automatically
      grafana_dashboard = "1"
    }
    annotations = {
      "dashboard/subdirectory" = "${each.value}"
    }
  }

  data = {
    for dashboard_file in fileset("${path.module}/dashboards/${each.value}", "*.json") :
    dashboard_file => file("${path.module}/dashboards/${each.value}/${dashboard_file}")
  }
}


resource "kubernetes_manifest" "grafana-ingress-route" {
  manifest = {
    apiVersion = "traefik.containo.us/v1alpha1"
    kind       = "IngressRoute"
    metadata = {
      name      = "grafana-ingress-route"
      namespace = var.namespace
    }
    spec = {
      entryPoints = ["websecure"]
      routes = [
        {
          kind  = "Rule"
          match = "Host(`${var.external-url}`) && PathPrefix(`/monitoring`)"
          services = [
            {
              name      = "nebari-grafana"
              port      = 80
              namespace = var.namespace
            }
          ]
        }
      ]
    }
  }
}
