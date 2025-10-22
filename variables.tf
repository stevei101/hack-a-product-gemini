# variables.tf

variable "gcp_project_id" {
  description = "The GCP project ID to create resources in."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to create resources in."
  default     = "us-central1"
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

variable "tfc_workspace_prefix" {
  description = "The prefix for Terraform Cloud workspace names."
  type        = string
  default     = "hack-a-product-gemini"
}

variable "cluster_name" {
  description = "The name of the GKE cluster."
  type        = string
  default     = "product-mindset-dev"
}

variable "POSTGRES_PASSWORD" {
  description = "The password for the PostgreSQL database."
  type        = string
  sensitive   = true
}

variable "NIM_API_KEY" {
  description = "The API key for NVIDIA NIM."
  type        = string
  sensitive   = true
}

