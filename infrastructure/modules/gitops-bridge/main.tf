# GitOps Bridge - passes Terraform metadata to ArgoCD via K8s Secret annotations
# This enables ApplicationSet cluster generator to template Helm values dynamically

resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

resource "kubernetes_secret" "gitops_bridge" {
  metadata {
    name      = "cluster-metadata"
    namespace = kubernetes_namespace.argocd.metadata[0].name
    labels = {
      "argocd.argoproj.io/secret-type" = "cluster"
      "environment"                     = var.metadata["environment"]
    }
    annotations = var.metadata
  }

  data = {
    name   = var.cluster_name
    server = "https://kubernetes.default.svc"
    config = jsonencode({
      tlsClientConfig = {
        insecure = false
      }
    })
  }

  type = "Opaque"
}
