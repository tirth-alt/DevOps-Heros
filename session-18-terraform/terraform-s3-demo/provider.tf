terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Credentials are NOT written here. The provider reads them from the AWS CLI
# configuration (aws configure) or from environment variables.
provider "aws" {
  region = var.aws_region
}
