# Kafka via Strimzi operator on EKS
# Strimzi is deployed via Helm through GitOps
# This module prepares namespace and any AWS resources needed

resource "kubernetes_namespace" "kafka" {
  metadata {
    name = "kafka"
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}
