# Main Terraform configuration for The Product Mindset
terraform {
  required_version = ">= 1.1.0"

  cloud {
    organization = "disposable-org"

    workspaces {
      name = "hack-a-product"
    }
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 3.53"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# --- GCS Bucket for Static Website ---

resource "google_storage_bucket" "site" {
  name          = "${var.gcp_project_id}-frontend-bucket"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  labels = {
    environment = var.environment
  }
}

# --- Kubernetes Provider Configuration ---

data "google_container_cluster" "primary" {
  name     = "primary-cluster"
  location = var.gcp_region
}

provider "kubernetes" {
  host  = "https://"
  token = data.google_container_cluster.primary.endpoint

  cluster_ca_certificate = base64decode(data.google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

# --- Artifact Registry for Docker Images ---

resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.gcp_region
  repository_id = "app-images"
  description   = "Docker repository for application images"
  format        = "DOCKER"

  labels = {
    environment = var.environment
  }
}