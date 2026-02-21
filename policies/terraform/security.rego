# Terraform infrastructure security policies
package policy

import rego.v1

violations contains violation if {
	input.resource_type == "aws_s3_bucket"
	not input.values.server_side_encryption_configuration
	violation := {
		"rule": "s3-encryption",
		"message": "S3 buckets must have server-side encryption enabled",
		"severity": "critical",
	}
}

violations contains violation if {
	input.resource_type == "aws_s3_bucket"
	acl := input.values.acl
	acl == "public-read"
	violation := {
		"rule": "no-public-s3",
		"message": "S3 buckets must not have public-read ACL",
		"severity": "critical",
	}
}

violations contains violation if {
	input.resource_type == "aws_security_group_rule"
	input.values.cidr_blocks[_] == "0.0.0.0/0"
	input.values.type == "ingress"
	violation := {
		"rule": "no-open-ingress",
		"message": "Security group rules must not allow unrestricted ingress (0.0.0.0/0)",
		"severity": "critical",
	}
}

violations contains violation if {
	input.resource_type == "aws_db_instance"
	input.values.publicly_accessible == true
	violation := {
		"rule": "no-public-rds",
		"message": "RDS instances must not be publicly accessible",
		"severity": "critical",
	}
}

violations contains violation if {
	input.resource_type == "aws_db_instance"
	not input.values.storage_encrypted
	violation := {
		"rule": "rds-encryption",
		"message": "RDS instances must have storage encryption enabled",
		"severity": "high",
	}
}

violations contains violation if {
	input.resource_type == "aws_db_instance"
	not input.values.backup_retention_period
	violation := {
		"rule": "rds-backup",
		"message": "RDS instances must have automated backups enabled",
		"severity": "high",
	}
}

violations contains violation if {
	input.resource_type == "aws_eks_cluster"
	not input.values.encryption_config
	violation := {
		"rule": "eks-secrets-encryption",
		"message": "EKS clusters must encrypt secrets at rest with KMS",
		"severity": "high",
	}
}
