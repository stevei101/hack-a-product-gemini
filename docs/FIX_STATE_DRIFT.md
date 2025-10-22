# 🔧 Fix: Terraform State Drift - Resources Already Exist

## 🔴 Problem

```
Error: Error creating Network: googleapi: Error 409: The resource already exists, alreadyExists
```

**Root Cause:** Resources exist in GCP but aren't tracked in Terraform Cloud's state file.

---

## ✅ Solution Options

### **Option 1: Import Resources (Recommended)** ⭐

Import existing resources into Terraform state without destroying them.

#### **Step 1: Set Up Environment**

```bash
# In your local terminal or GCP Cloud Shell
export GCP_PROJECT_ID="free-project-1249"
export GCP_REGION="us-central1"
export TF_API_TOKEN="your-terraform-cloud-token"

# Configure Terraform Cloud credentials
cat > ~/.terraformrc << EOF
credentials "app.terraform.io" {
  token = "${TF_API_TOKEN}"
}
EOF
```

#### **Step 2: Clone and Initialize**

```bash
# Clone the repository
git clone https://github.com/stevei101/hack-a-product-gemini.git
cd hack-a-product-gemini
git checkout switch-to-google

# Initialize Terraform (connects to Terraform Cloud)
terraform init
```

#### **Step 3: Import Resources**

Run the import script:

```bash
export GCP_PROJECT_ID="free-project-1249"
./scripts/import-existing-resources.sh
```

Or manually import each resource:

```bash
# VPC Network
terraform import google_compute_network.vpc "projects/${GCP_PROJECT_ID}/global/networks/gke-network"

# Subnet
terraform import google_compute_subnetwork.subnet "projects/${GCP_PROJECT_ID}/regions/${GCP_REGION}/subnetworks/gke-subnet"

# GKE Cluster
terraform import google_container_cluster.primary "projects/${GCP_PROJECT_ID}/locations/${GCP_REGION}/clusters/primary-cluster"

# Node Pool
terraform import google_container_node_pool.primary_nodes "projects/${GCP_PROJECT_ID}/locations/${GCP_REGION}/clusters/primary-cluster/nodePools/primary-node-pool"

# GCS Bucket
terraform import google_storage_bucket.site "${GCP_PROJECT_ID}-frontend-bucket"

# Artifact Registry
terraform import google_artifact_registry_repository.docker_repo "projects/${GCP_PROJECT_ID}/locations/${GCP_REGION}/repositories/app-images"

# Service Account
terraform import google_service_account.gke_application_sa "projects/${GCP_PROJECT_ID}/serviceAccounts/gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# IAM Member
terraform import google_project_iam_member.app_storage_viewer "${GCP_PROJECT_ID} roles/storage.objectViewer serviceAccount:gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Service Account IAM Member
terraform import google_service_account_iam_member.gke_application_sa_impersonation "projects/${GCP_PROJECT_ID}/serviceAccounts/gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com roles/iam.workloadIdentityUser serviceAccount:${GCP_PROJECT_ID}.svc.id.goog[default/app-ksa]"
```

#### **Step 4: Verify Import**

```bash
# Check that state is synced
terraform plan

# Should show: "No changes. Your infrastructure matches the configuration."
```

#### **Step 5: Re-run GitHub Actions**

Once imports are complete, push an empty commit to trigger the workflow:

```bash
git commit --allow-empty -m "trigger: retry after importing resources"
git push origin switch-to-google
```

---

### **Option 2: Use Terraform Import Blocks** (Terraform 1.5+)

Add import blocks to your configuration (cleaner approach):

Create `imports.tf`:

```hcl
import {
  to = google_compute_network.vpc
  id = "projects/${var.gcp_project_id}/global/networks/gke-network"
}

import {
  to = google_compute_subnetwork.subnet
  id = "projects/${var.gcp_project_id}/regions/${var.gcp_region}/subnetworks/gke-subnet"
}

import {
  to = google_container_cluster.primary
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/clusters/primary-cluster"
}

import {
  to = google_container_node_pool.primary_nodes
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/clusters/primary-cluster/nodePools/primary-node-pool"
}

import {
  to = google_storage_bucket.site
  id = "${var.gcp_project_id}-frontend-bucket"
}

import {
  to = google_artifact_registry_repository.docker_repo
  id = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/repositories/app-images"
}

import {
  to = google_service_account.gke_application_sa
  id = "projects/${var.gcp_project_id}/serviceAccounts/gke-application-sa@${var.gcp_project_id}.iam.gserviceaccount.com"
}
```

Then run:
```bash
terraform plan -generate-config-out=generated.tf
terraform apply
```

After successful import, delete `imports.tf`.

---

### **Option 3: Destroy and Recreate** (Clean Slate)

If you don't need to preserve the existing resources:

#### **⚠️ Warning: This will delete all infrastructure!**

```bash
# In GCP Cloud Shell
export GCP_PROJECT_ID="free-project-1249"
export GCP_REGION="us-central1"

# Delete GKE cluster (takes ~10 minutes)
gcloud container clusters delete primary-cluster --region=${GCP_REGION} --quiet

# Delete VPC network
gcloud compute networks subnets delete gke-subnet --region=${GCP_REGION} --quiet
gcloud compute networks delete gke-network --quiet

# Delete service account
gcloud iam service-accounts delete gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com --quiet

# Delete GCS bucket
gcloud storage rm -r gs://${GCP_PROJECT_ID}-frontend-bucket

# Delete Artifact Registry
gcloud artifacts repositories delete app-images --location=${GCP_REGION} --quiet

echo "✅ Resources deleted. Now re-run GitHub Actions workflow."
```

Then push to trigger workflow:
```bash
git commit --allow-empty -m "trigger: redeploy after cleanup"
git push origin switch-to-google
```

---

## 🎯 **Recommended Approach**

**For this situation, use Option 1 (Import)** because:
- ✅ No downtime
- ✅ Preserves existing resources
- ✅ Faster than recreating GKE cluster
- ✅ Maintains data in GCS bucket

**Use Option 3 (Destroy) only if:**
- ❌ No important data exists
- ❌ You want a completely clean state
- ❌ Resources are in a bad state

---

## 🔍 Why This Happened

Possible causes:
1. **State Reset** - Terraform Cloud workspace state was deleted/reset
2. **Different Workspace** - Using a different TFC workspace than where resources were created
3. **Manual Creation** - Resources created manually or via gcloud instead of Terraform
4. **Failed Import** - Previous import attempt failed partway through

---

## 📋 **Quick Import Commands** (Copy-Paste)

```bash
# Set your project
export GCP_PROJECT_ID="free-project-1249"

# Import all resources
terraform import google_compute_network.vpc "projects/${GCP_PROJECT_ID}/global/networks/gke-network"
terraform import google_compute_subnetwork.subnet "projects/${GCP_PROJECT_ID}/regions/us-central1/subnetworks/gke-subnet"
terraform import google_container_cluster.primary "projects/${GCP_PROJECT_ID}/locations/us-central1/clusters/primary-cluster"
terraform import google_container_node_pool.primary_nodes "projects/${GCP_PROJECT_ID}/locations/us-central1/clusters/primary-cluster/nodePools/primary-node-pool"
terraform import google_storage_bucket.site "${GCP_PROJECT_ID}-frontend-bucket"
terraform import google_artifact_registry_repository.docker_repo "projects/${GCP_PROJECT_ID}/locations/us-central1/repositories/app-images"
terraform import google_service_account.gke_application_sa "projects/${GCP_PROJECT_ID}/serviceAccounts/gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
terraform import google_project_iam_member.app_storage_viewer "${GCP_PROJECT_ID} roles/storage.objectViewer serviceAccount:gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
terraform import google_service_account_iam_member.gke_application_sa_impersonation "projects/${GCP_PROJECT_ID}/serviceAccounts/gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com roles/iam.workloadIdentityUser serviceAccount:${GCP_PROJECT_ID}.svc.id.goog[default/app-ksa]"

# Verify
terraform plan
```

---

## ✅ **Success Indicators**

After importing, `terraform plan` should show:

```
No changes. Your infrastructure matches the configuration.
```

Or minimal changes like:
- Adding missing labels
- Updating computed attributes
- Adding missing metadata

**If you see resources being created/destroyed**, something went wrong - review the import IDs.

---

## 🚨 Troubleshooting

### **Error: "resource not found"**
- Resource doesn't exist in GCP
- Check resource name/ID matches exactly
- Verify project ID and region are correct

### **Error: "unauthorized"**
- TF_API_TOKEN not set or invalid
- Service account lacks permissions
- Check Workload Identity Federation is working

### **Import succeeds but plan shows changes**
- Normal for computed attributes
- Review changes - if they're just labels/metadata, safe to apply
- If shows recreation, check import ID format

---

**Last Updated:** October 22, 2025  
**Status:** Ready to fix state drift

