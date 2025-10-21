# terraform/iam-policies.tf

# --- GitHub Actions Workload Identity Federation ---

# Service Account for GitHub Actions
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-runner"
  display_name = "GitHub Actions Runner"
  description  = "Service account for GitHub Actions to deploy resources"
}

# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Workload Identity Pool for GitHub Actions"
}

# Workload Identity Pool Provider for GitHub
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions Provider"
  description                        = "Workload Identity Provider for GitHub Actions"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allow the GitHub Actions service account to be impersonated by the Workload Identity Pool
resource "google_service_account_iam_member" "github_actions_impersonation" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_organization}/${var.github_repository}"
}

# --- Service Account Permissions ---

# Grant Storage Admin role to the service account for GCS bucket management
resource "google_project_iam_member" "storage_admin" {
  project = var.gcp_project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Grant Kubernetes Engine Admin role for GKE cluster management
resource "google_project_iam_member" "kubernetes_admin" {
  project = var.gcp_project_id
  role    = "roles/container.admin"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Grant Artifact Registry Admin role for Docker image management

resource "google_project_iam_member" "artifact_registry_admin" {

  project = var.gcp_project_id

  role    = "roles/artifactregistry.admin"

  member  = "serviceAccount:${google_service_account.github_actions.email}"

}



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
