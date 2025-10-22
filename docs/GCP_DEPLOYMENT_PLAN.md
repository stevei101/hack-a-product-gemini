# 🚀 Google Cloud Platform Deployment Plan

## Executive Summary

This document provides a comprehensive plan to complete the Terraform Cloud and GitHub Actions deployment for the `hack-a-product-gemini` project targeting Google Cloud Platform (GCP).

**Current Status:** ✅ Infrastructure 80% deployed, ❌ Blocking API and K8s issues

---

## 📊 Current State Analysis

### ✅ What's Working

- Terraform Cloud backend configured correctly  
- GCP authentication passing from GitHub Secrets
- Resources successfully created:
  - ✅ VPC Network (`gke-network`)
  - ✅ Subnet (`gke-subnet`)
  - ✅ GKE Cluster (`primary-cluster`) - 11 minutes creation time
  - ✅ GKE Node Pool (`primary-node-pool`)
  - ✅ GCS Bucket (`*-frontend-bucket`)
  - ✅ Artifact Registry (`app-images`)
  - ✅ Service Account (`gke-application-sa`)

### ❌ Current Blockers

| Issue | Severity | Status |
|-------|----------|--------|
| Cloud Resource Manager API disabled | 🔴 CRITICAL | **REQUIRES MANUAL ACTION** |
| Kubernetes provider connection error | 🔴 CRITICAL | ✅ **FIXED IN CODE** |
| Variable name mismatches | 🟡 WARNING | ✅ **FIXED** |

---

## 🎯 Phase 1: Fix Immediate Blockers

### Step 1.1: Enable Required GCP APIs ⚠️ **ACTION REQUIRED**

**Problem:** Cloud Resource Manager API and potentially other APIs are disabled

**Solution:** Run these commands with your GCP credentials:

```bash
# Set your project ID
export GCP_PROJECT_ID="YOUR_PROJECT_ID"  # Replace with your actual project ID

# Enable all required APIs
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com \
  storage-api.googleapis.com \
  storage-component.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  cloudapis.googleapis.com \
  --project=$GCP_PROJECT_ID

# Verify APIs are enabled
gcloud services list --enabled --project=$GCP_PROJECT_ID
```

**Alternative - Via GCP Console:**

1. Go to: https://console.cloud.google.com/apis/library?project=YOUR_PROJECT_ID
2. Enable these APIs:
   - ✅ Cloud Resource Manager API
   - ✅ Kubernetes Engine API
   - ✅ Artifact Registry API
   - ✅ Compute Engine API
   - ✅ Cloud Storage API
   - ✅ IAM Service Account Credentials API

### Step 1.2: Code Fixes (Already Applied) ✅

**Fixed Issues:**
- ✅ Removed unused variables (`github_org`/`github_repo` - reserved for future OIDC integration)
- ✅ Kubernetes provider uncommented and properly configured
- ✅ Data source dependency added for GKE cluster

---

## 🏗️ Phase 2: Complete Infrastructure Deployment

### Step 2.1: Re-run Terraform Apply

After enabling APIs, push code to trigger new run:

```bash
git add .
git commit -m "fix: Enable K8s provider and fix variable names"
git push origin switch-to-google
```

**Expected Outcome:**
- All 10 resources successfully created
- Kubernetes service account created in GKE cluster
- IAM bindings applied correctly

### Step 2.2: Verify Infrastructure

```bash
# Verify GKE cluster
gcloud container clusters list --project=$GCP_PROJECT_ID

# Get kubectl credentials
gcloud container clusters get-credentials primary-cluster \
  --region=us-central1 \
  --project=$GCP_PROJECT_ID

# Verify nodes
kubectl get nodes

# Verify service account
kubectl get serviceaccount app-ksa -n default
```

---

## 📦 Phase 3: Complete CI/CD Pipeline

### Current Gap Analysis

**What AWS project has that GCP project needs:**

| Component | AWS Project (`hack-a-product`) | GCP Project (`hack-a-product-gemini`) | Status |
|-----------|-------------------------------|---------------------------------------|--------|
| **Terraform Location** | `terraform/` subdirectory | Root directory | ⚠️ Needs reorganization |
| **Workflow Structure** | Separate terraform workflow | Terraform-only workflow | ⚠️ Needs build/deploy jobs |
| **Build Job** | ✅ Builds frontend/backend | ❌ Missing | 🔴 **REQUIRED** |
| **Docker Build** | ✅ Automated | ❌ Missing | 🔴 **REQUIRED** |
| **Helm Deployment** | ✅ Automated | ❌ Missing | 🔴 **REQUIRED** |
| **Static Site Deploy** | ✅ To S3/CloudFront | ❌ Missing GCS deploy | 🔴 **REQUIRED** |

### Step 3.1: Restructure Project (Optional but Recommended)

Move Terraform files to subdirectory to match AWS pattern:

```bash
# Create terraform subdirectory
mkdir -p terraform

# Move terraform files
mv main.tf variables.tf gke.tf iam-policies.tf terraform/

# Update workflow to use terraform directory
# working-directory: ./terraform
```

### Step 3.2: Create Complete Deployment Workflow

Based on the removed `deploy.yml`, create a comprehensive workflow with:

1. **Job 1: Build and Test**
   - Build frontend (Bun + React)
   - Build backend (Python + FastAPI)
   - Run tests
   - Upload build artifacts

2. **Job 2: Deploy Infrastructure** (Current terraform.yml)
   - Initialize Terraform Cloud
   - Plan and Apply infrastructure
   - Wait for GKE cluster ready

3. **Job 3: Build and Push Docker Images**
   - Login to Artifact Registry
   - Build frontend image
   - Build backend image
   - Push to GAR

4. **Job 4: Deploy to GKE**
   - Configure kubectl
   - Deploy with Helm charts
   - Set environment secrets

5. **Job 5: Deploy Static Site**
   - Download build artifacts
   - Sync to GCS bucket
   - Set bucket permissions

### Step 3.3: Implementation Plan

**Option A: Single Comprehensive Workflow** (Recommended - matches deploy.yml pattern)

Create `.github/workflows/deploy-gcp.yml` with all jobs in sequence.

**Option B: Separate Workflows** (Current approach)

- Keep `terraform.yml` for infrastructure
- Add `build-deploy.yml` for application deployment

---

## 🔐 Phase 4: Secrets and Configuration

### Required GitHub Secrets

Verify all secrets are configured at:
`https://github.com/stevei101/hack-a-product-gemini/settings/secrets/actions`

| Secret Name | Purpose | Status |
|-------------|---------|--------|
| `TF_API_TOKEN` | Terraform Cloud authentication | ✅ Required |
| `GCP_SA_KEY` | GCP service account JSON | ✅ Have |
| `GCP_PROJECT_ID` | Your GCP project ID | ✅ Have |
| `POSTGRES_PASSWORD` | Database password | ✅ Required |
| `NIM_API_KEY` | NVIDIA NIM API key | ✅ Required |
| `NIM_BASE_URL` | NVIDIA NIM base URL | ⚠️ Check if needed |
| `NIM_MODEL` | NVIDIA NIM model name | ⚠️ Check if needed |

### Terraform Cloud Workspace Variables

**If using remote execution mode**, also set in Terraform Cloud:

- `GOOGLE_CREDENTIALS` (env) = Contents of GCP_SA_KEY
- `TF_VAR_gcp_project_id` (env) = Your project ID

**Note:** Current workflow passes these from GitHub Actions, so TFC variables are optional for CI/CD runs.

---

## 📋 Phase 5: Application Deployment Components

### Components Needed (from deploy.yml)

1. **Docker Images:**
   ```yaml
   # Frontend: React + TypeScript + Bun (Vite powered by Bun, not Node)
   FROM node:18
   # Backend: Python 3.11 + FastAPI + uv
   FROM python:3.11
   ```

2. **Helm Charts:**
   - `charts/frontend/` - Already exists ✅
   - `charts/backend/` - Already exists ✅
   - Update values.yaml for GKE

3. **GCS Bucket Sync:**
   ```bash
   gsutil rsync -d -r dist/ gs://$PROJECT_ID-frontend-bucket
   ```

### Step 5.1: Verify Helm Charts

Check that Helm charts are GKE-compatible:

```bash
# Lint charts
helm lint ./charts/frontend
helm lint ./charts/backend

# Dry-run
helm template frontend ./charts/frontend
helm template backend ./charts/backend
```

### Step 5.2: Update Helm Values for GKE

Update `charts/*/values.yaml` to reference Artifact Registry:

```yaml
image:
  repository: us-central1-docker.pkg.dev/PROJECT_ID/app-images/frontend
  tag: latest
  pullPolicy: IfNotPresent

serviceAccount:
  create: true
  name: app-ksa
  annotations:
    iam.gke.io/gcp-service-account: gke-application-sa@PROJECT_ID.iam.gserviceaccount.com
```

---

## 🎯 Phase 6: Testing and Validation

### Step 6.1: Infrastructure Validation

```bash
# Check all resources created
gcloud compute networks list
gcloud container clusters list
gcloud artifacts repositories list
gcloud storage buckets list

# Verify IAM bindings
gcloud iam service-accounts list
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:gke-application-sa@*"
```

### Step 6.2: Application Validation

```bash
# Check deployments
kubectl get deployments -A

# Check services
kubectl get services -A

# Check pods
kubectl get pods -A

# Test backend API
kubectl port-forward svc/backend 8000:8000 -n dev
curl http://localhost:8000/health

# Test frontend
kubectl port-forward svc/frontend 3000:80 -n dev
curl http://localhost:3000
```

### Step 6.3: End-to-End Test

1. Make a code change
2. Create PR → Verify plan posts to PR
3. Merge to switch-to-google → Verify:
   - Terraform applies
   - Docker images build and push
   - Helm deploys to GKE
   - Static site deploys to GCS
   - Application is accessible

---

## 📈 Success Criteria

### Phase 1 Success ✅
- [ ] All GCP APIs enabled
- [ ] Terraform apply completes without errors
- [ ] All 10 resources created successfully

### Phase 2 Success ✅
- [ ] GKE cluster accessible via kubectl
- [ ] Kubernetes service account created
- [ ] Workload Identity configured

### Phase 3 Success ✅
- [ ] Complete CI/CD workflow implemented
- [ ] Docker images build automatically
- [ ] Helm deploys to GKE automatically
- [ ] Static site deploys to GCS automatically

### Phase 4 Success ✅
- [ ] Application accessible via LoadBalancer
- [ ] Backend API responding
- [ ] Frontend serving from GCS
- [ ] Database connected and functional

---

## 🚨 Known Issues and Mitigations

### Issue 1: GKE Cluster Takes 10+ Minutes to Create

**Mitigation:**
- Use separate workflow for infrastructure vs application
- Cache Terraform state in Terraform Cloud
- Only run terraform on infrastructure changes

### Issue 2: Workload Identity Requires Careful Configuration

**Mitigation:**
- Verify service account annotations in Kubernetes
- Check IAM bindings in GCP
- Test with `gcloud iam service-accounts` commands

### Issue 3: First Deployment Always Has Some Issues

**Mitigation:**
- Use `terraform apply -target` to deploy resources incrementally
- Test locally with kind/minikube first
- Enable verbose logging in GitHub Actions

---

## 📚 Reference Comparison

### AWS Project vs GCP Project

| Aspect | AWS (`hack-a-product`) | GCP (`hack-a-product-gemini`) |
|--------|------------------------|------------------------------|
| **Container Registry** | ECR | Artifact Registry ✅ |
| **Kubernetes** | EKS | GKE ✅ |
| **Static Hosting** | S3 + CloudFront | GCS + Load Balancer |
| **Terraform Backend** | Terraform Cloud ✅ | Terraform Cloud ✅ |
| **Workflow Structure** | Separate terraform | Combined terraform ⚠️ |
| **File Organization** | `terraform/` subdirectory | Root directory ⚠️ |
| **Deployment Automation** | Complete ✅ | Partial ⚠️ |

---

## 🎯 Recommended Next Steps

### Immediate (Today)
1. ⚡ **Enable GCP APIs** (see Step 1.1)
2. ⚡ **Push code changes** to trigger new Terraform run
3. ⚡ **Verify infrastructure** creation completes

### Short Term (This Week)
4. 📦 Implement complete build/deploy workflow
5. 🐳 Add Docker image build jobs
6. ⚓ Add Helm deployment jobs
7. 🌐 Add GCS static site deployment

### Medium Term (Next Week)
8. 🧪 Add comprehensive testing
9. 📊 Add monitoring and logging
10. 🔒 Harden security (secrets management, network policies)
11. 📖 Update documentation

---

## 📞 Support Resources

- **Terraform Cloud Docs:** https://developer.hashicorp.com/terraform/cloud-docs
- **GKE Docs:** https://cloud.google.com/kubernetes-engine/docs
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Reference AWS Project:** `/Users/stevenirvin/Documents/GitHub/hack-a-product`
- **Removed deploy.yml:** `/Users/stevenirvin/Desktop/deploy.yml`

---

## ✅ Checklist

### Phase 1: Fix Blockers
- [x] Fix variable name mismatches
- [x] Uncomment Kubernetes provider
- [ ] Enable Cloud Resource Manager API ⚠️ **ACTION REQUIRED**
- [ ] Enable all other required GCP APIs

### Phase 2: Complete Infrastructure
- [ ] Re-run terraform apply
- [ ] Verify all resources created
- [ ] Test kubectl access

### Phase 3: Build CI/CD
- [ ] Implement build job
- [ ] Implement Docker build/push
- [ ] Implement Helm deployment
- [ ] Implement GCS deployment

### Phase 4: Validate
- [ ] Test end-to-end flow
- [ ] Verify application accessible
- [ ] Monitor logs and metrics

---

**Created:** October 22, 2025  
**Last Updated:** October 22, 2025  
**Status:** 🟡 In Progress - Phase 1 Active

