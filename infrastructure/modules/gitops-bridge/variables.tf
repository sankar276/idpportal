variable "cluster_name" {
  type = string
}

variable "metadata" {
  description = "GitOps bridge metadata to pass as cluster secret annotations"
  type        = map(string)
}

variable "tags" {
  type    = map(string)
  default = {}
}
