# 🔐 Workload Identity Federation Setup

## Overview

This project uses **Workload Identity Federation (WIF)** to authenticate GitHub Actions with Google Cloud Platform without storing long-lived service account keys.

**Benefits:**
- ✅ No service account keys stored in GitHub
- ✅ Automatic token rotation
- ✅ Fine-grained access control per repository
- ✅ Better security posture
- ✅ Follows Google Cloud best practices

---

## Setup Complete ✅

The Workload Identity Federation has been configured with the following components:

### Service Account
- **Name:** `github-actions-runner`
- **Email:** `github-actions-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com`
- **Role:** `roles/owner` (granted for hackathon; use least-privilege roles in production)

### Workload Identity Pool
- **Pool ID:** `github-actions-pool`
- **Location:** `global`
- **Purpose:** Allows GitHub Actions to authenticate via OIDC tokens

### Workload Identity Provider
- **Provider ID:** `github-actions-provider`
- **Type:** OIDC
- **Issuer:** `https://token.actions.githubusercontent.com`
- **Repository:** `stevei101/hack-a-product-gemini`

---

## GitHub Secrets Required

Configure these secrets at:
**https://github.com/stevei101/hack-a-product-gemini/settings/secrets/actions**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider` | WIF provider resource path |
| `WIF_SERVICE_ACCOUNT` | `github-actions-runner@YOUR_PROJECT_ID.iam.gserviceaccount.com` | Service account email |
| `GCP_PROJECT_ID` | `YOUR_PROJECT_ID` | Your GCP project ID |
| `TF_API_TOKEN` | `<your-terraform-cloud-token>` | Terraform Cloud API token |
| `POSTGRES_PASSWORD` | `<your-password>` | PostgreSQL database password |
| `NIM_API_KEY` | `<your-api-key>` | NVIDIA NIM API key |

---

## How It Works

### Authentication Flow

```
┌─────────────────┐
│ GitHub Actions  │
│   Workflow      │
└────────┬────────┘
         │
         │ 1. Request OIDC token from GitHub
         ▼
┌─────────────────┐
│ GitHub OIDC     │
│ Token Service   │
└────────┬────────┘
         │
         │ 2. Return signed JWT token
         ▼
┌─────────────────┐
│ google-github-  │
│ actions/auth@v2 │
└────────┬────────┘
         │
         │ 3. Exchange OIDC token for GCP access token
         ▼
┌─────────────────┐
│ Workload        │
│ Identity Pool   │
└────────┬────────┘
         │
         │ 4. Validate token & repository
         ▼
┌─────────────────┐
│ GCP STS         │
│ (Token Service) │
└────────┬────────┘
         │
         │ 5. Generate short-lived access token
         ▼
┌─────────────────┐
│ Service Account │
│ Impersonation   │
└────────┬────────┘
         │
         │ 6. Access GCP resources
         ▼
┌─────────────────┐
│ GCP Resources   │
│ (GKE, GCS, etc) │
└─────────────────┘
```

### Workflow Configuration

The `.github/workflows/terraform.yml` workflow uses WIF with these key steps:

```yaml
permissions:
  id-token: write  # Required for OIDC token

steps:
  - name: Authenticate to Google Cloud via Workload Identity Federation
    id: auth
    uses: google-github-actions/auth@v2
    with:
      workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
      service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      token_format: 'access_token'
      access_token_lifetime: '3600s'
  
  - name: Export GCP Credentials for Terraform
    run: |
      echo "GOOGLE_OAUTH_ACCESS_TOKEN=${{ steps.auth.outputs.access_token }}" >> $GITHUB_ENV
```

---

## Security Considerations

### Access Control

The WIF provider is configured with an attribute condition:
```
attribute.repository == 'stevei101/hack-a-product-gemini'
```

This means **only** workflows from this specific repository can authenticate.

### Token Lifetime

- Access tokens are short-lived (60 minutes)
- Automatically rotated by Google
- No persistent credentials stored

### IAM Roles

Current configuration grants `roles/owner` for hackathon simplicity.

**For Production, use least-privilege roles:**
```bash
export GCP_PROJECT_ID="YOUR_PROJECT_ID"

# Remove owner role
gcloud projects remove-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:github-actions-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/owner"

# Grant specific roles
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:github-actions-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:github-actions-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/compute.networkAdmin"

# Add other specific roles as needed
```

---

## Troubleshooting

### Error: "Permission denied on resource"

**Cause:** Service account lacks required IAM role  
**Fix:** Grant specific role to service account

```bash
export GCP_PROJECT_ID="YOUR_PROJECT_ID"

gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:github-actions-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/REQUIRED_ROLE"
```

### Error: "Unable to get valid credentials"

**Cause:** WIF_PROVIDER or WIF_SERVICE_ACCOUNT secret incorrect  
**Fix:** Verify secrets match the values in this document

### Error: "Attribute condition not satisfied"

**Cause:** Workflow running from wrong repository or branch  
**Fix:** Verify workflow is running from `stevei101/hack-a-product-gemini`

### Error: "Token expired"

**Cause:** Access token lifetime exceeded (rare)  
**Fix:** Token automatically refreshes; retry the workflow

---

## Maintenance

### Rotate Service Account

To rotate the service account:

```bash
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
export PROJECT_NUMBER=$(gcloud projects describe ${GCP_PROJECT_ID} --format='value(projectNumber)')

# Create new service account
gcloud iam service-accounts create github-actions-runner-new \
  --display-name="GitHub Actions Runner (New)" \
  --project=${GCP_PROJECT_ID}

# Grant same roles
gcloud projects add-iam-policy-binding ${GCP_PROJECT_ID} \
  --member="serviceAccount:github-actions-runner-new@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/owner"

# Update WIF binding
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-runner-new@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/YOUR_ORG/YOUR_REPO"

# Update GitHub secret WIF_SERVICE_ACCOUNT
# Test workflow
# Delete old service account
```

### Update Repository Access

To allow another repository to use WIF:

```bash
export GCP_PROJECT_ID="YOUR_PROJECT_ID"
export PROJECT_NUMBER=$(gcloud projects describe ${GCP_PROJECT_ID} --format='value(projectNumber)')
export NEW_REPO="YOUR_ORG/another-repo"

# Update provider attribute condition
gcloud iam workload-identity-pools providers update-oidc github-actions-provider \
  --workload-identity-pool="github-actions-pool" \
  --location="global" \
  --attribute-condition="attribute.repository == '${NEW_REPO}'"

# Add IAM binding for new repo
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-runner@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/${NEW_REPO}"
```

---

## Resources

- [Google Cloud Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)

---

**Created:** October 22, 2025  
**Last Updated:** October 22, 2025  
**Status:** ✅ Active and Configured

