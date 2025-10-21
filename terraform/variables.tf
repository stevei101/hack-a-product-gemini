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

variable "github_org" {
  description = "The name of your GitHub organization."
  type        = string
}

variable "github_repo" {
  description = "The name of your GitHub repository."
  type        = string
}

variable "tfc_organization" {
  description = "The name of your Terraform Cloud organization."
  type        = string
  default     = "disposable-org"
}

variable "tfc_workspace_prefix" {
  description = "The prefix for Terraform Cloud workspace names."
  type        = string
  default     = "product-mindset"
}

variable "cluster_name" {
  description = "The name of the EKS cluster."
  type        = string
  default     = "product-mindset-dev"
}

variable "AWS_ACCESS_KEY_ID" {
  description = "AWS access key ID"
  type        = string
  sensitive   = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "AWS secret access key"
  type        = string
  sensitive   = true
}
