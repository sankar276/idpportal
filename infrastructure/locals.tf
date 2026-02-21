# GitOps Bridge metadata assembly
# Terraform outputs → K8s Secret annotations → ApplicationSet cluster generator → Helm values
locals {
  name   = var.cluster_name
  region = var.region

  vpc_cidr = var.vpc_cidr
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = merge(var.tags, {
    "kubernetes.io/cluster/${var.cluster_name}" = "owned"
  })

  # GitOps Bridge - metadata passed to ArgoCD ApplicationSet via cluster secret annotations
  gitops_bridge_metadata = {
    cluster_name     = var.cluster_name
    environment      = var.environment
    region           = var.region
    vpc_id           = module.vpc.vpc_id
    account_id       = data.aws_caller_identity.current.account_id

    # IAM Role ARNs for Pod Identity
    iam_role_arn_external_secrets  = module.iam.external_secrets_role_arn
    iam_role_arn_external_dns      = module.iam.external_dns_role_arn
    iam_role_arn_cert_manager      = module.iam.cert_manager_role_arn
    iam_role_arn_vault             = var.enable_vault ? module.vault[0].vault_role_arn : ""

    # Service endpoints
    vault_addr              = var.enable_vault ? "http://vault.vault.svc.cluster.local:8200" : ""
    kafka_bootstrap_servers = var.enable_kafka ? "kafka-kafka-bootstrap.kafka.svc.cluster.local:9092" : ""

    # GitOps
    gitops_repo_url    = var.gitops_repo_url
    gitops_repo_branch = var.gitops_repo_branch

    # Domain
    domain_name = var.domain_name

    # Addons enabled flags
    enable_vault  = tostring(var.enable_vault)
    enable_kafka  = tostring(var.enable_kafka)
  }
}

data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}
