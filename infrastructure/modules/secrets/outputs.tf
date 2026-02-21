output "config_secret_arn" {
  value = aws_secretsmanager_secret.config.arn
}

output "github_app_secret_arn" {
  value = aws_secretsmanager_secret.github_app.arn
}

output "argocd_secret_arn" {
  value = aws_secretsmanager_secret.argocd.arn
}

output "keycloak_secret_arn" {
  value = aws_secretsmanager_secret.keycloak.arn
}
