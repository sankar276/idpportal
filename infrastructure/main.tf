module "vpc" {
  source = "./modules/vpc"

  cluster_name = var.cluster_name
  environment  = var.environment
  vpc_cidr     = local.vpc_cidr
  azs          = local.azs
  tags         = local.tags
}

module "eks" {
  source = "./modules/eks"

  cluster_name       = var.cluster_name
  cluster_version    = var.cluster_version
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  node_min_size      = var.node_min_size
  node_max_size      = var.node_max_size
  node_desired_size  = var.node_desired_size
  tags               = local.tags
}

module "iam" {
  source = "./modules/iam"

  cluster_name    = var.cluster_name
  oidc_provider   = module.eks.oidc_provider
  oidc_issuer_url = module.eks.oidc_issuer_url
  tags            = local.tags
}

module "secrets" {
  source = "./modules/secrets"

  cluster_name = var.cluster_name
  environment  = var.environment
  tags         = local.tags
}

module "vault" {
  source = "./modules/vault"
  count  = var.enable_vault ? 1 : 0

  cluster_name    = var.cluster_name
  oidc_provider   = module.eks.oidc_provider
  oidc_issuer_url = module.eks.oidc_issuer_url
  tags            = local.tags
}

module "kafka" {
  source = "./modules/kafka"
  count  = var.enable_kafka ? 1 : 0

  cluster_name = var.cluster_name
  tags         = local.tags
}

module "gitops_bridge" {
  source = "./modules/gitops-bridge"

  cluster_name = var.cluster_name
  metadata     = local.gitops_bridge_metadata
  tags         = local.tags

  depends_on = [module.eks]
}
