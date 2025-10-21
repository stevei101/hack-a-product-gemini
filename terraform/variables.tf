# variables.tf

variable "aws_region" {
  description = "The AWS region to create resources in."
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "The name of the S3 bucket. Must be globally unique."
  type        = string
}

variable "environment" {
  description = "The environment (e.g., 'development', 'production')."
  default     = "development"
}

variable "github_organization" {
  description = "The name of your GitHub organization."
  type        = string
}

variable "github_repository" {
  description = "The name of your GitHub repository."
  type        = string
}

variable "project_name" {
  description = "The name of the project, used for naming resources."
  type        = string
  default     = "product-mindset"
}
