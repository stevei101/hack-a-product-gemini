#!/bin/bash
#
# This script performs the one-time setup for Google Cloud Workload Identity
# Federation to allow GitHub Actions to securely authenticate with your GCP project.
#
# v2: Adds an explicit attribute-condition to the provider creation to fix
#     the "INVALID_ARGUMENT" error seen in some gcloud environments.
#
# INSTRUCTIONS:
# 1. Open Google Cloud Shell.
# 2. Create a new file named setup_wif.sh and paste this content into it.
# 3. Update the variables in the "CONFIGURATION" section below.
# 4. Make the script executable: chmod +x setup_wif.sh
# 5. Run the script: ./setup_wif.sh

set -e
set -u

# --- CONFIGURATION ---
# UPDATE THESE VARIABLES WITH YOUR SPECIFIC VALUES
GCP_PROJECT_ID="free-project-1249"
GITHUB_ORG="stevei101"
GITHUB_REPO="hack-a-product-gemini"

# --- SCRIPT ---
GSA_NAME="github-actions-runner"
WIF_POOL_ID="github-actions-pool"
WIF_PROVIDER_ID="github-actions-provider"
GSA_EMAIL="${GSA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

echo "--- Setting project to ${GCP_PROJECT_ID} ---"
gcloud config set project "${GCP_PROJECT_ID}"

echo "--- Enabling required Google Cloud APIs ---"
gcloud services enable iam.googleapis.com \
    iamcredentials.googleapis.com \
    sts.googleapis.com

echo "--- Creating Service Account [${GSA_NAME}] (if it doesn't exist) ---"
gcloud iam service-accounts describe "${GSA_EMAIL}" >/dev/null 2>&1 || \
    gcloud iam service-accounts create "${GSA_NAME}" \
        --display-name="GitHub Actions Runner" \
        --description="Service account for GitHub Actions to deploy resources"

echo "--- Granting 'Owner' role to Service Account ---"
# For simplicity in a hackathon, we grant Owner. In production, you would
# grant specific, least-privilege roles (e.g., roles/container.admin).
gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
    --member="serviceAccount:${GSA_EMAIL}" \
    --role="roles/owner"

echo "--- Creating Workload Identity Pool [${WIF_POOL_ID}] (if it doesn't exist) ---"
gcloud iam workload-identity-pools describe "${WIF_POOL_ID}" --location="global" >/dev/null 2>&1 || \
    gcloud iam workload-identity-pools create "${WIF_POOL_ID}" \
        --location="global" \
        --display-name="GitHub Actions Pool" \
        --description="Workload Identity Pool for GitHub Actions"

echo "--- Getting full Workload Identity Pool name ---"
WORKLOAD_IDENTITY_POOL_NAME=$(gcloud iam workload-identity-pools describe "${WIF_POOL_ID}" \
    --location="global" \
    --format="value(name)")

echo "--- Creating Workload Identity Pool Provider [${WIF_PROVIDER_ID}] ---"
gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER_ID}" \
    --workload-identity-pool="${WIF_POOL_ID}" \
    --location="global" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="attribute.repository == '${GITHUB_ORG}/${GITHUB_REPO}'"

echo "--- Allowing GitHub Actions to impersonate the Service Account ---"
gcloud iam service-accounts add-iam-policy-binding "${GSA_EMAIL}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_NAME}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

echo "--- SETUP COMPLETE ---"
echo "You can now re-run your GitHub Actions workflow."