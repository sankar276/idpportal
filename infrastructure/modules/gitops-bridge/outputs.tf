output "argocd_namespace" {
  value = kubernetes_namespace.argocd.metadata[0].name
}

output "cluster_secret_name" {
  value = kubernetes_secret.gitops_bridge.metadata[0].name
}
