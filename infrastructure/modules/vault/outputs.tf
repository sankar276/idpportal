output "vault_role_arn" {
  value = module.vault_role.iam_role_arn
}

output "kms_key_id" {
  value = aws_kms_key.vault.key_id
}

output "kms_key_arn" {
  value = aws_kms_key.vault.arn
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.vault.name
}
