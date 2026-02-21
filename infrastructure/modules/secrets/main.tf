# AWS Secrets Manager - bootstrap secrets only (Vault takes over for app secrets)

resource "aws_secretsmanager_secret" "config" {
  name        = "idpportal/config"
  description = "IDP Portal bootstrap configuration"
  tags        = var.tags
}

resource "aws_secretsmanager_secret_version" "config" {
  secret_id = aws_secretsmanager_secret.config.id
  secret_string = jsonencode({
    cluster_name = var.cluster_name
    environment  = var.environment
  })
}

resource "aws_secretsmanager_secret" "github_app" {
  name        = "idpportal/github-app"
  description = "GitHub App credentials for Backstage and ArgoCD"
  tags        = var.tags
}

resource "aws_secretsmanager_secret" "argocd" {
  name        = "idpportal/argocd"
  description = "ArgoCD admin credentials and repo secrets"
  tags        = var.tags
}

resource "aws_secretsmanager_secret" "keycloak" {
  name        = "idpportal/keycloak"
  description = "Keycloak admin and OIDC client secrets"
  tags        = var.tags
}
