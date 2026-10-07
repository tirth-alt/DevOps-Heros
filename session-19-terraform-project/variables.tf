variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used in the names of all resources"
  type        = string
  default     = "session19"
}

variable "vpc_cidr" {
  description = "IP range of the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "subnet_cidr" {
  description = "IP range of the public subnet (must sit inside the VPC range)"
  type        = string
  default     = "10.20.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type. Check which types your account's free tier covers."
  type        = string
  default     = "t3.micro"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name (lowercase letters, numbers and hyphens)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be 3 to 63 characters of lowercase letters, numbers and hyphens."
  }
}
