# HashiCorp Vault on EKS with AWS KMS auto-unseal

resource "aws_kms_key" "vault" {
  description             = "Vault auto-unseal key for ${var.cluster_name}"
  deletion_window_in_days = 7
  tags                    = var.tags
}

resource "aws_kms_alias" "vault" {
  name          = "alias/${var.cluster_name}-vault"
  target_key_id = aws_kms_key.vault.key_id
}

# IAM role for Vault to access KMS for auto-unseal
module "vault_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.44"

  role_name = "${var.cluster_name}-vault"

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider
      namespace_service_accounts = ["vault:vault"]
    }
  }

  role_policy_arns = {
    vault_kms = aws_iam_policy.vault_kms.arn
  }

  tags = var.tags
}

resource "aws_iam_policy" "vault_kms" {
  name        = "${var.cluster_name}-vault-kms"
  description = "Vault KMS auto-unseal policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:DescribeKey",
        ]
        Resource = [aws_kms_key.vault.arn]
      }
    ]
  })
}

# DynamoDB table for Vault storage backend
resource "aws_dynamodb_table" "vault" {
  name         = "${var.cluster_name}-vault-storage"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Path"
  range_key    = "Key"

  attribute {
    name = "Path"
    type = "S"
  }

  attribute {
    name = "Key"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}
