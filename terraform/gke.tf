# terraform/gke.tf

# --- GKE Cluster ---

# VPC Network for GKE
resource "google_compute_network" "vpc" {
  name                    = "gke-network"
  auto_create_subnetworks = false
}

# Subnetwork for GKE
resource "google_compute_subnetwork" "subnet" {
  name          = "gke-subnet"
  ip_cidr_range = "10.10.0.0/24"
  network       = google_compute_network.vpc.self_link
  region        = var.gcp_region
}

# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = "primary-cluster"
  location = var.gcp_region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.self_link
  subnetwork = google_compute_subnetwork.subnet.self_link
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

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
