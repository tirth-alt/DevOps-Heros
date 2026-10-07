resource "aws_s3_bucket" "demo" {
  bucket = var.bucket_name

  # Lets "terraform destroy" delete the bucket even if it still contains objects
  force_destroy = true

  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "Session18"
  }
}

# Block every form of public access to the bucket
resource "aws_s3_bucket_public_access_block" "demo" {
  bucket = aws_s3_bucket.demo.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
