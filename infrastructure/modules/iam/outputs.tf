output "external_secrets_role_arn" {
  value = module.external_secrets_role.iam_role_arn
}

output "external_dns_role_arn" {
  value = module.external_dns_role.iam_role_arn
}

output "cert_manager_role_arn" {
  value = module.cert_manager_role.iam_role_arn
}
