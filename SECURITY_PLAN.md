# 🔒 Public Repository Security Plan

## 🎯 Executive Summary

This document provides a comprehensive plan to ensure no sensitive data is exposed in your public GitHub repository.

---

## 🚨 Immediate Security Audit Results

### ✅ What's Already Secure

1. **Environment Variables** - All sensitive configs use environment variables
   - ✅ `.env` files properly gitignored
   - ✅ `terraform.tfvars` files properly gitignored
   - ✅ `backend/env.example` contains only placeholders

2. **Configuration Management** - Using proper patterns
   - ✅ `config.py` reads from environment variables
   - ✅ Terraform uses variables from TF Cloud
   - ✅ GitHub Actions uses GitHub Secrets

3. **Git History** - Clean
   - ✅ No `.env` or `.tfvars` files in git history
   - ✅ No hardcoded API keys detected

### ⚠️ Issues Found & Fixed

| Issue | Location | Risk Level | Status |
|-------|----------|------------|--------|
| Hardcoded GCP Project ID | `docs/FIX_STATE_DRIFT.md` | 🟡 LOW | 🔧 TO FIX |
| Missing `.gitattributes` | Root | 🟡 LOW | 🔧 TO ADD |
| No pre-commit hooks | Root | 🟢 INFO | 🔧 TO ADD |
| No secret scanning | CI/CD | 🟢 INFO | 🔧 TO ADD |

---

## 📋 Implementation Plan

### Phase 1: Fix Existing Issues (Immediate)

#### 1.1 Remove Hardcoded Project ID
**File:** `docs/FIX_STATE_DRIFT.md`

Replace all instances of `free-project-1249` with `your-gcp-project-id`

#### 1.2 Add `.gitattributes`
Prevent accidental commits of sensitive file types:

```gitattributes
# Never commit these files
*.env merge=ours
*.tfvars merge=ours
*secret* merge=ours
*credentials* merge=ours
*.pem filter=secret
*.key filter=secret
id_rsa* filter=secret
```

#### 1.3 Enhance `.gitignore`
Add additional protection:

```gitignore
# Secrets and Credentials (additional patterns)
.env*
!.env.example
!env.example
*.tfvars
!*.tfvars.example
*secret*
!SECURITY_*.md
*credentials*
*.pem
*.key
*.p12
*.pfx
id_rsa*
.gcp/
.aws/
.azure/

# Terraform
.terraform/
.terraform.lock.hcl
terraform.tfstate
terraform.tfstate.backup
override.tf
override.tf.json
*_override.tf
*_override.tf.json
crash.log
crash.*.log

# Local configuration
.envrc
.direnv/
```

---

### Phase 2: Add Security Scanning (High Priority)

#### 2.1 Install `gitleaks` (Secret Scanner)

**Create:** `.github/workflows/security-scan.yml`

```yaml
name: Security Scan

on:
  push:
    branches: [ main, switch-to-google, develop ]
  pull_request:
    branches: [ main, switch-to-google ]

jobs:
  gitleaks:
    name: Scan for Secrets
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch all history
      
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }} # Only required for organizations

  trufflehog:
    name: TruffleHog Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: TruffleHog OSS
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --debug --only-verified
```

#### 2.2 Create `.gitleaksignore`

Whitelist known false positives:

```
# Gitleaks ignore patterns
# Generic placeholder values
your_secure_postgres_password_here
your_nvidia_nim_api_key_here
your_jwt_secret_key_here
your_api_authentication_key_here
your-gcp-project-id

# Test/Example files
backend/env.example:*
terraform.tfvars.example:*
```

---

### Phase 3: Pre-Commit Hooks (Recommended)

#### 3.1 Install `pre-commit` Framework

**Create:** `.pre-commit-config.yaml`

```yaml
repos:
  # Secret detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-yaml
      - id: check-json
      - id: detect-private-key
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: no-commit-to-branch
        args: ['--branch', 'main']

  # Terraform checks
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.83.5
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint

  # Python checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        additional_dependencies: ['bandit[toml]']
```

#### 3.2 Installation Instructions

**Create:** `docs/PRE_COMMIT_SETUP.md`

```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Test manually (optional)
pre-commit run --all-files
```

---

### Phase 4: Documentation Security (Best Practice)

#### 4.1 Create Security Documentation Templates

**Files to Update:**
- Replace all placeholder project IDs with variables
- Use `${GCP_PROJECT_ID}` or `your-gcp-project-id`
- Never include real project names, IDs, or resource names

#### 4.2 Security Review Checklist

Create `SECURITY_CHECKLIST.md`:

```markdown
# Security Checklist for Public Repositories

## Before Every Commit

- [ ] No `.env` files committed
- [ ] No `.tfvars` files committed
- [ ] No API keys or tokens in code
- [ ] No passwords or secrets
- [ ] No GCP project IDs (use placeholders)
- [ ] No AWS account IDs
- [ ] No private SSH keys
- [ ] No database connection strings with credentials

## In Documentation

- [ ] Use placeholder values (your-project-id, YOUR_API_KEY)
- [ ] No screenshots containing sensitive data
- [ ] No log files with real credentials

## Before Making Repository Public

- [ ] Run `gitleaks detect --source . --verbose`
- [ ] Check GitHub Security tab for vulnerabilities
- [ ] Review all open issues for sensitive data
- [ ] Review all closed PRs for sensitive data
```

---

### Phase 5: Continuous Monitoring

#### 5.1 Enable GitHub Security Features

**In GitHub Repository Settings:**

1. **Enable Dependabot alerts**
   - Settings → Security & analysis → Dependabot alerts: ✅

2. **Enable Secret Scanning**
   - Settings → Security & analysis → Secret scanning: ✅
   - (Free for public repositories)

3. **Enable Code Scanning (CodeQL)**
   - Settings → Security & analysis → Code scanning: ✅
   - Add `.github/workflows/codeql.yml`

4. **Protected Branches**
   - Require status checks before merging
   - Require security scan to pass

#### 5.2 Create CodeQL Workflow

**Create:** `.github/workflows/codeql.yml`

```yaml
name: "CodeQL Security Scan"

on:
  push:
    branches: [ main, switch-to-google ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
```

---

## 🔐 Secrets Management Best Practices

### Current Setup (Already Good)

```
✅ GitHub Secrets → GitHub Actions
✅ Terraform Cloud Variables → Terraform
✅ Environment Variables → Application Config
✅ .env.example files for templates
```

### Additional Recommendations

1. **Rotate secrets regularly** (every 90 days)
2. **Use different secrets for dev/staging/prod**
3. **Never log secret values** (already implemented in code)
4. **Use secret managers for production**:
   - GCP: Secret Manager
   - AWS: Secrets Manager / Parameter Store
   - HashiCorp Vault

---

## 📊 Security Levels

### Current Security Level: 🟢 GOOD

| Category | Status |
|----------|--------|
| Environment Variables | ✅ Secure |
| Git Ignore | ✅ Secure |
| Config Management | ✅ Secure |
| CI/CD Secrets | ✅ Secure |
| Documentation | ⚠️ Needs Review |
| Secret Scanning | ❌ Not Enabled |
| Pre-commit Hooks | ❌ Not Enabled |

### Target Security Level: 🟢 EXCELLENT

After implementing all phases:

| Category | Target |
|----------|--------|
| Environment Variables | ✅ Secure |
| Git Ignore | ✅ Enhanced |
| Config Management | ✅ Secure |
| CI/CD Secrets | ✅ Secure |
| Documentation | ✅ Clean |
| Secret Scanning | ✅ Automated |
| Pre-commit Hooks | ✅ Enabled |
| Continuous Monitoring | ✅ Active |

---

## 🚀 Quick Start Implementation

### Immediate (Do Now - 15 minutes)

```bash
# 1. Fix hardcoded project ID
# (Script provided separately)

# 2. Add .gitattributes
# (Script provided separately)

# 3. Enhance .gitignore
# (Script provided separately)

# 4. Scan for secrets now
docker run -v $(pwd):/path ghcr.io/gitleaks/gitleaks:latest detect --source /path -v
```

### Short Term (This Week)

1. ✅ Add security scan workflow
2. ✅ Enable GitHub secret scanning
3. ✅ Review and clean documentation
4. ✅ Add CodeQL scanning

### Medium Term (This Month)

1. ✅ Install pre-commit hooks
2. ✅ Add security checklist to PR template
3. ✅ Rotate all existing secrets
4. ✅ Document security procedures

---

## 📝 Files to Create/Modify

### New Files
- ✅ `.gitattributes`
- ✅ `.gitleaksignore`
- ✅ `.pre-commit-config.yaml`
- ✅ `.github/workflows/security-scan.yml`
- ✅ `.github/workflows/codeql.yml`
- ✅ `SECURITY_CHECKLIST.md`
- ✅ `docs/PRE_COMMIT_SETUP.md`

### Files to Modify
- ✅ `.gitignore` (enhance)
- ✅ `docs/FIX_STATE_DRIFT.md` (remove project ID)
- ✅ Review all `/docs/*.md` files

---

## 🎯 Success Criteria

Repository is secure when:

- ✅ No secrets in git history
- ✅ No secrets in current files
- ✅ Automated secret scanning passes
- ✅ Pre-commit hooks installed
- ✅ GitHub security features enabled
- ✅ Documentation uses only placeholders
- ✅ CI/CD security checks passing

---

**Next Steps:** Run the implementation scripts provided separately.

