variable "cluster_name" {
  type = string
}

variable "cluster_version" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "node_instance_types" {
  type    = list(string)
  default = ["m6i.xlarge"]
}

variable "node_min_size" {
  type    = number
  default = 3
}

variable "node_max_size" {
  type    = number
  default = 6
}

variable "node_desired_size" {
  type    = number
  default = 3
}

variable "cluster_endpoint_public_access" {
  description = "Whether the EKS API endpoint is publicly accessible. Set to false for production."
  type        = bool
  default     = true
}

variable "kms_key_arn" {
  description = "KMS key ARN for encrypting K8s secrets at rest"
  type        = string
  default     = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
