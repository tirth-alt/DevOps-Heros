variable "aws_region" {
  description = "AWS region where the bucket is created"
  type        = string
  default     = "ap-south-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name (lowercase letters, numbers and hyphens only)"
  type        = string
}

variable "environment" {
  description = "Environment tag applied to the bucket"
  type        = string
  default     = "dev"
}
