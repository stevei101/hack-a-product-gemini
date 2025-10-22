# terraform/gke.tf

# --- GKE Cluster ---

# VPC Network for GKE
resource "google_compute_network" "vpc" {
  name                    = "gke-network"
  auto_create_subnetworks = false

  lifecycle {
    # Prevent destruction of the network if it causes issues
    prevent_destroy = false
  }
}

# Subnetwork for GKE
resource "google_compute_subnetwork" "subnet" {
  name          = "gke-subnet"
  ip_cidr_range = "10.10.0.0/24"
  network       = google_compute_network.vpc.self_link
  region        = var.gcp_region

  lifecycle {
    # Prevent destruction of the subnet if it causes issues
    prevent_destroy = false
  }
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "primary-cluster"
  location = var.gcp_region

  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false # Allow destruction

  network    = google_compute_network.vpc.self_link
  subnetwork = google_compute_subnetwork.subnet.self_link

  workload_identity_config {
    workload_pool = "${var.gcp_project_id}.svc.id.goog"
  }
}

# GKE Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-medium"
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# --- Kubernetes Service Account for the Application ---

resource "kubernetes_service_account" "app_ksa" {
  metadata {
    name      = "app-ksa"
    namespace = "default" # This should be parameterized for different environments
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.gke_application_sa.email
    }
  }
}

# Allow the Kubernetes Service Account to impersonate the Google Service Account
resource "google_service_account_iam_member" "gke_application_sa_impersonation" {
  service_account_id = google_service_account.gke_application_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.gcp_project_id}.svc.id.goog[${kubernetes_service_account.app_ksa.metadata[0].namespace}/${kubernetes_service_account.app_ksa.metadata[0].name}]"
}
