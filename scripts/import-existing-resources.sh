#!/bin/bash
#
# Import Existing GCP Resources into Terraform State
#
# This script imports resources that already exist in GCP into Terraform Cloud state
#
# Prerequisites:
#   - export GCP_PROJECT_ID="your-project-id"
#   - export TF_API_TOKEN="your-terraform-cloud-token"
#   - terraform init (already done)

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"

# Validate
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID environment variable is required"
    echo "Usage: export GCP_PROJECT_ID=\"your-project-id\" && ./import-existing-resources.sh"
    exit 1
fi

echo "🔄 Importing existing GCP resources into Terraform state..."
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Function to import resource
import_resource() {
    local resource_name=$1
    local resource_id=$2
    
    echo "⏳ Importing ${resource_name}..."
    if terraform import "${resource_name}" "${resource_id}" 2>&1 | grep -q "successfully imported"; then
        echo "✅ ${resource_name} imported"
    else
        echo "⚠️  ${resource_name} import failed or already imported"
    fi
    echo ""
}

# Import VPC Network
import_resource "google_compute_network.vpc" "projects/${PROJECT_ID}/global/networks/gke-network"

# Import Subnet
import_resource "google_compute_subnetwork.subnet" "projects/${PROJECT_ID}/regions/${REGION}/subnetworks/gke-subnet"

# Import GKE Cluster
import_resource "google_container_cluster.primary" "projects/${PROJECT_ID}/locations/${REGION}/clusters/primary-cluster"

# Import Node Pool
import_resource "google_container_node_pool.primary_nodes" "projects/${PROJECT_ID}/locations/${REGION}/clusters/primary-cluster/nodePools/primary-node-pool"

# Import GCS Bucket
import_resource "google_storage_bucket.site" "${PROJECT_ID}-frontend-bucket"

# Import Artifact Registry
import_resource "google_artifact_registry_repository.docker_repo" "projects/${PROJECT_ID}/locations/${REGION}/repositories/app-images"

# Import Service Account
import_resource "google_service_account.gke_application_sa" "projects/${PROJECT_ID}/serviceAccounts/gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Import IAM Member (this one is tricky - check if it exists first)
echo "⏳ Checking IAM member..."
import_resource "google_project_iam_member.app_storage_viewer" "${PROJECT_ID} roles/storage.objectViewer serviceAccount:gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Import Service Account IAM Member
SA_ID="projects/${PROJECT_ID}/serviceAccounts/gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com"
import_resource "google_service_account_iam_member.gke_application_sa_impersonation" "${SA_ID} roles/iam.workloadIdentityUser serviceAccount:${PROJECT_ID}.svc.id.goog[default/app-ksa]"

echo ""
echo "✅ Import complete!"
echo ""
echo "Next steps:"
echo "1. Run 'terraform plan' to verify state matches GCP"
echo "2. If plan shows 0 changes, state is synced ✅"
echo "3. If plan shows changes, review and apply if needed"

