# Pod Identity IAM roles for platform workloads

# External Secrets Operator - reads from AWS Secrets Manager
module "external_secrets_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.44"

  role_name = "${var.cluster_name}-external-secrets"

  attach_external_secrets_policy        = true
  external_secrets_secrets_manager_arns = ["arn:aws:secretsmanager:*:*:secret:idpportal/*"]

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider
      namespace_service_accounts = ["external-secrets:external-secrets"]
    }
  }

  tags = var.tags
}

# External DNS - manages Route53 records
module "external_dns_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.44"

  role_name = "${var.cluster_name}-external-dns"

  attach_external_dns_policy    = true
  external_dns_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider
      namespace_service_accounts = ["external-dns:external-dns"]
    }
  }

  tags = var.tags
}

# Cert Manager - DNS01 challenges via Route53
module "cert_manager_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.44"

  role_name = "${var.cluster_name}-cert-manager"

  attach_cert_manager_policy    = true
  cert_manager_hosted_zone_arns = ["arn:aws:route53:::hostedzone/*"]

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider
      namespace_service_accounts = ["cert-manager:cert-manager"]
    }
  }

  tags = var.tags
}
