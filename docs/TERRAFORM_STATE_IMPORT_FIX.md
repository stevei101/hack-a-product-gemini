# Terraform State Import Fix

## Problem

Terraform Cloud was showing errors when trying to create resources that already exist in GCP:

```
Error: Error creating Network: googleapi: Error 409: The resource 'projects/***/global/networks/gke-network' already exists, alreadyExists
```

This happens when resources exist in GCP but aren't tracked in Terraform Cloud's state file.

## Root Cause

Your GCP infrastructure was created in a previous Terraform run, but the state wasn't properly synced to Terraform Cloud. When GitHub Actions tried to run `terraform apply`, it attempted to create resources that already exist.

## Solution Implemented

### 1. **Created `imports.tf`** ✅

Added automatic import blocks for all existing resources:
- VPC Network (`gke-network`)
- Subnet (`gke-subnet`)
- GKE Cluster (`primary-cluster`)
- GKE Node Pool (`primary-node-pool`)
- GCS Bucket (`<project-id>-frontend-bucket`)
- Artifact Registry (`app-images`)
- Service Account (`gke-application-sa`)

These import blocks will automatically bring existing resources into Terraform state during the next `terraform plan/apply`.

### 2. **Updated Terraform Version** ✅

- **Updated** `main.tf` to require Terraform `>= 1.5.0` (needed for import blocks)
- **Updated** GitHub Actions workflow to explicitly use Terraform `1.6.0`

### 3. **Added Lifecycle Protection** ✅

Added lifecycle blocks to critical network resources to prevent accidental destruction.

### 4. **Fixed Variable Issues** ✅

- Added `bucket_name` variable with default value
- Updated bucket creation logic to support both explicit and auto-generated names

## Terraform Cloud Variables

Make sure these variables are set in your Terraform Cloud workspace:

| Variable | Value | Type | Sensitive |
|----------|-------|------|-----------|
| `gcp_project_id` | Your GCP Project ID | terraform | No |
| `POSTGRES_PASSWORD` | Database password | terraform | Yes |
| `NIM_API_KEY` | NVIDIA NIM API key | terraform | Yes |
| `bucket_name` | *(optional - leave empty for auto-generation)* | terraform | No |

### For `bucket_name` variable:

You have two options:

1. **Don't add it** - The code will auto-generate: `<your-project-id>-frontend-bucket`
2. **Add it explicitly** - Set to empty string `""` or your desired bucket name

## Next Steps

### 1. Commit and Push Changes

```bash
git add .
git commit -m "fix: Add import blocks for existing GCP resources and update Terraform version"
git push origin switch-to-google
```

### 2. Monitor GitHub Actions

The next GitHub Actions run will:
1. Import existing resources into Terraform state
2. Run `terraform plan` to verify state matches reality
3. Apply any remaining changes

### 3. Expected Outcome

After the import:
- ✅ No more "already exists" errors
- ✅ Terraform state synced with actual GCP infrastructure
- ✅ Future runs will update resources instead of trying to recreate them

## How Import Blocks Work (Terraform 1.5+)

Import blocks were introduced in Terraform 1.5 and provide a declarative way to import existing resources:

```hcl
import {
  id = "projects/my-project/global/networks/gke-network"
  to = google_compute_network.vpc
}
```

When Terraform runs:
1. It checks if the resource exists in state
2. If not, it imports the resource using the provided ID
3. Future runs will manage the imported resource normally

## Troubleshooting

### If imports fail:

Check if resources actually exist:
```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# List networks
gcloud compute networks list --project=$GCP_PROJECT_ID

# List GKE clusters
gcloud container clusters list --project=$GCP_PROJECT_ID

# List buckets
gcloud storage buckets list --project=$GCP_PROJECT_ID
```

### If you need to manually import:

Use the script provided:
```bash
export GCP_PROJECT_ID="your-project-id"
./scripts/import-existing-resources.sh
```

### If you want to start fresh:

Delete all resources and let Terraform recreate them:
```bash
# WARNING: This will delete your infrastructure!
terraform destroy -auto-approve
terraform apply -auto-approve
```

## Files Changed

1. ✅ `imports.tf` - New file with import blocks
2. ✅ `main.tf` - Updated Terraform version requirement
3. ✅ `gke.tf` - Added lifecycle blocks
4. ✅ `variables.tf` - Added `bucket_name` variable
5. ✅ `terraform.tfvars.example` - Updated example
6. ✅ `.github/workflows/terraform.yml` - Pinned Terraform version

## References

- [Terraform Import Blocks Documentation](https://developer.hashicorp.com/terraform/language/import)
- [Google Provider Import Examples](https://registry.terraform.io/providers/hashicorp/google/latest/docs/guides/version_3_upgrade)

