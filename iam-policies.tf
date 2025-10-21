# terraform/iam-policies.tf

# --- GKE Application Service Account ---

# Dedicated Service Account for the GKE application workload
resource "google_service_account" "gke_application_sa" {
  account_id   = "gke-application-sa"
  display_name = "GKE Application Service Account"
  description  = "Service account for the application running in GKE"
}

# Grant Storage Object Viewer role to the application service account
resource "google_project_iam_member" "app_storage_viewer" {
  project = var.gcp_project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.gke_application_sa.email}"
}

