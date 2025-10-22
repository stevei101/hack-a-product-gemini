# 🔐 Security Best Practices

This document outlines the security measures implemented in this repository to protect sensitive information.

---

## 🎯 Principles

1. **No Hardcoded Secrets** - Never commit API keys, passwords, or tokens
2. **No Project-Specific Information** - Use environment variables and placeholders
3. **Environment Variables** - Store sensitive data in GitHub Secrets and environment variables
4. **Parameterized Scripts** - All scripts accept configuration via environment variables
5. **Documentation Placeholders** - Use `[PROJECT_ID]`, `YOUR_PROJECT_ID`, etc. in docs

---

## ✅ What's Protected

### **Never in Repository:**
- ❌ GCP Project IDs
- ❌ Service Account Emails (with project IDs)
- ❌ API Keys
- ❌ Passwords
- ❌ Access Tokens
- ❌ Private Keys or JSON Key Files
- ❌ GitHub Organization/Repository Names (in code)
- ❌ Workload Identity Federation Provider Paths

### **Where Sensitive Data Should Be:**
- ✅ **GitHub Secrets** - For CI/CD workflows
  - `TF_API_TOKEN`
  - `GCP_PROJECT_ID`
  - `WIF_PROVIDER`
  - `WIF_SERVICE_ACCOUNT`
  - `POSTGRES_PASSWORD`
  - `NIM_API_KEY`

- ✅ **Environment Variables** - For local development
  ```bash
  export GCP_PROJECT_ID="your-project-id"
  export GCP_REGION="us-central1"
  ```

- ✅ **Terraform Cloud Workspace** - For infrastructure secrets (optional)
  - `GOOGLE_CREDENTIALS` (if running manually in TFC)

---

## 📝 Script Best Practices

### **Before (❌ Bad):**
```bash
#!/bin/bash
PROJECT_ID="free-project-1249"
REGION="us-central1"
SA_EMAIL="gke-application-sa@free-project-1249.iam.gserviceaccount.com"
```

### **After (✅ Good):**
```bash
#!/bin/bash
# Configuration from environment variables
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Validate required variables
if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is required"
    echo "Usage: export GCP_PROJECT_ID=\"your-project-id\""
    exit 1
fi
```

---

## 📋 Files Reviewed and Secured

| File | Status | Notes |
|------|--------|-------|
| `setup_wif.sh` | ✅ Secured | Uses `YOUR_GCP_PROJECT_ID` placeholder |
| `scripts/verify-gcp-infrastructure.sh` | ✅ Secured | Requires `GCP_PROJECT_ID` env var |
| `docs/WORKLOAD_IDENTITY_FEDERATION.md` | ✅ Secured | All IDs replaced with placeholders |
| `docs/GCP_DEPLOYMENT_PLAN.md` | ✅ Secured | Uses `YOUR_PROJECT_ID` |
| `docs/INFRASTRUCTURE_VERIFICATION.md` | ✅ Secured | All commands use `${GCP_PROJECT_ID}` |
| `.github/workflows/terraform.yml` | ✅ Secured | Uses GitHub Secrets only |
| `main.tf` | ✅ Secured | No hardcoded values |
| `variables.tf` | ✅ Secured | No default sensitive values |
| `gke.tf` | ✅ Secured | Uses variables only |
| `iam-policies.tf` | ✅ Secured | Uses variables only |

---

## 🔍 How to Check for Leaks

### **Search for Sensitive Patterns:**
```bash
# Check for project IDs
grep -r "free-project-1249" . --exclude-dir=.git

# Check for email addresses with project IDs
grep -r "@free-project-1249.iam.gserviceaccount.com" . --exclude-dir=.git

# Check for project numbers
grep -r "771642754691" . --exclude-dir=.git

# Should return: 0 matches in code files
```

### **Files That May Contain Project Info (OK):**
- `.git/` directory - Git history (not pushed)
- This documentation file (explaining security)
- README examples (if clearly marked as examples)

---

## 🛠️ Proper Usage Examples

### **Running Verification Script:**
```bash
# Set your project ID
export GCP_PROJECT_ID="your-actual-project-id"

# Optional customization
export GCP_REGION="us-central1"
export CLUSTER_NAME="primary-cluster"

# Run the script
./scripts/verify-gcp-infrastructure.sh
```

### **Using gcloud Commands:**
```bash
# Always use variables
export GCP_PROJECT_ID="your-project-id"

# Good ✅
gcloud config set project ${GCP_PROJECT_ID}
gcloud services list --project=${GCP_PROJECT_ID}

# Bad ❌
gcloud config set project free-project-1249
```

### **Documentation Examples:**
```markdown
# Good ✅
export GCP_PROJECT_ID="your-project-id"
gcloud services enable compute.googleapis.com --project=${GCP_PROJECT_ID}

# Bad ❌
gcloud services enable compute.googleapis.com --project=free-project-1249
```

---

## 🚨 What To Do If Secrets Are Leaked

If you accidentally commit sensitive information:

1. **Immediately Rotate Credentials**
   ```bash
   # For service account keys
   gcloud iam service-accounts keys delete KEY_ID \
     --iam-account=SA_EMAIL
   
   # Create new key
   gcloud iam service-accounts keys create new-key.json \
     --iam-account=SA_EMAIL
   ```

2. **Remove from Git History**
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # Or create a new repository and push clean code
   ```

3. **Update GitHub Secrets**
   - Go to repository Settings → Secrets
   - Update affected secrets

4. **Revoke Terraform Cloud Token**
   - Generate new token in Terraform Cloud
   - Update `TF_API_TOKEN` secret

---

## ✅ Pre-Commit Checklist

Before committing, always check:

- [ ] No hardcoded project IDs
- [ ] No hardcoded email addresses (with domains)
- [ ] No API keys or tokens
- [ ] No passwords
- [ ] Scripts use environment variables
- [ ] Documentation uses placeholders
- [ ] Run `terraform fmt` (automated via pre-commit hook)
- [ ] Search for your project ID: `grep -r "your-project-id" .`

---

## 📚 Reference

### **Placeholder Conventions:**

| Use Case | Placeholder Format |
|----------|-------------------|
| Project ID in code | `${GCP_PROJECT_ID}` or `${PROJECT_ID}` |
| Project ID in docs | `[PROJECT_ID]` or `YOUR_PROJECT_ID` or `your-project-id` |
| Project Number | `[PROJECT_NUMBER]` or `PROJECT_NUMBER` |
| Service Account | `SA_NAME@[PROJECT_ID].iam.gserviceaccount.com` |
| GitHub Org/Repo | `[YOUR_ORG]/[YOUR_REPO]` |
| Region | `${GCP_REGION}` (with us-central1 default) |
| Cluster Name | `${CLUSTER_NAME}` (with primary-cluster default) |

### **Environment Variables:**

| Variable | Purpose | Required |
|----------|---------|----------|
| `GCP_PROJECT_ID` | Your GCP project ID | ✅ Yes |
| `GCP_REGION` | GCP region | Optional (default: us-central1) |
| `CLUSTER_NAME` | GKE cluster name | Optional (default: primary-cluster) |
| `SA_NAME` | Service account name | Optional (default: gke-application-sa) |

---

## 🎯 GitHub Secrets Configuration

Required secrets in GitHub repository settings:

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `WIF_PROVIDER` | Workload Identity Federation provider | `projects/NUMBER/locations/global/...` |
| `WIF_SERVICE_ACCOUNT` | Service account email | `SA_NAME@PROJECT_ID.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | GCP project ID | `your-project-id` |
| `TF_API_TOKEN` | Terraform Cloud API token | `user.xxxxx.atlasv1.xxxxx` |
| `POSTGRES_PASSWORD` | Database password | `<password>` |
| `NIM_API_KEY` | NVIDIA NIM API key | `<api-key>` |

**Configure at:**
`https://github.com/YOUR_ORG/YOUR_REPO/settings/secrets/actions`

---

## 🔐 Workload Identity Federation

Using WIF eliminates the need to store service account keys:

**Benefits:**
- ✅ No long-lived credentials in GitHub
- ✅ Automatic token rotation
- ✅ Fine-grained access control
- ✅ Better security posture

**Setup:** See `docs/WORKLOAD_IDENTITY_FEDERATION.md`

---

## 📖 Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google Cloud Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Terraform Cloud Sensitive Variables](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/variables)
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)

---

**Last Updated:** October 22, 2025  
**Status:** ✅ All sensitive data secured

