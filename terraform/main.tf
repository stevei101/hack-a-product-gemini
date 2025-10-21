# Main Terraform configuration for The Product Mindset (v0.12 compatible)
terraform {
  required_version = ">= 0.12"

  required_providers {
    aws = "~> 3.0"
  }
}

# Configure the AWS Provider
# S3 Bucket for Static Website Hosting
resource "aws_s3_bucket" "site" {
  bucket = var.bucket_name

  tags = {
    Name        = "Static Site Bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "site_public_access_block" {
  bucket = aws_s3_bucket.site.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_website_configuration" "site_config" {
  bucket = aws_s3_bucket.site.id
}
