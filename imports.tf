# imports.tf
# Import existing GCP resources into Terraform state
# This file uses Terraform 1.5+ import blocks to handle existing resources

# Import VPC Network if it exists
import {
  id = "projects/${var.gcp_project_id}/global/networks/gke-network"
  to = google_compute_network.vpc
}

# Import Subnet if it exists
import {
  id = "projects/${var.gcp_project_id}/regions/${var.gcp_region}/subnetworks/gke-subnet"
  to = google_compute_subnetwork.subnet
}

# Import GKE Cluster if it exists
import {
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/clusters/primary-cluster"
  to = google_container_cluster.primary
}

# Import Node Pool if it exists
import {
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/clusters/primary-cluster/nodePools/primary-node-pool"
  to = google_container_node_pool.primary_nodes
}

# Import GCS Bucket if it exists
import {
  id = "${var.gcp_project_id}-frontend-bucket"
  to = google_storage_bucket.site
}

# Import Artifact Registry if it exists
import {
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/repositories/app-images"
  to = google_artifact_registry_repository.docker_repo
}

# Import Service Account if it exists
import {
  id = "projects/${var.gcp_project_id}/serviceAccounts/gke-application-sa@${var.gcp_project_id}.iam.gserviceaccount.com"
  to = google_service_account.gke_application_sa
}

