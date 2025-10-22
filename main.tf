# Main Terraform configuration for The Product Mindset
terraform {
  required_version = ">= 1.1.0"

  # Terraform Cloud backend configuration
  cloud {
    organization = var.tfc_organization
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

# Get cluster credentials
data "google_container_cluster" "primary" {
  name     = google_container_cluster.primary.name
  location = google_container_cluster.primary.location

  depends_on = [google_container_cluster.primary]
}

data "google_client_config" "default" {}

# Configure Kubernetes provider to connect to GKE
provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
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