terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Credentials are never written here. The provider reads them from the
# AWS CLI configuration (aws configure) or from environment variables.
provider "aws" {
  region = var.aws_region

  # Every resource that supports tags gets these automatically
  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "Terraform"
      Session   = "19"
    }
  }
}
