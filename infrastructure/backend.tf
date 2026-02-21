terraform {
  backend "s3" {
    bucket         = "idpportal-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "idpportal-terraform-locks"
    encrypt        = true
  }
}
