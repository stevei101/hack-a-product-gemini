# 🔒 Security Checklist

Use this checklist before every commit and before making the repository public.

---

## ✅ Before Every Commit

### Code & Configuration
- [ ] No `.env` files committed (only `.env.example`)
- [ ] No `.tfvars` files committed (only `.tfvars.example`)
- [ ] No API keys, tokens, or passwords in code
- [ ] No hardcoded secrets (use environment variables)
- [ ] No real GCP project IDs (use `your-gcp-project-id`)
- [ ] No AWS account IDs or ARNs with real data
- [ ] No database connection strings with actual credentials
- [ ] No private SSH keys or certificates

### Documentation
- [ ] Use placeholder values in docs (`YOUR_API_KEY`, `your-project-id`)
- [ ] No screenshots containing sensitive data
- [ ] No log files with real credentials or tokens
- [ ] No commit messages with sensitive information

### Dependencies
- [ ] All dependencies up to date
- [ ] No known vulnerabilities in dependencies
- [ ] Lock files committed (bun.lock, requirements.txt)

---

## ✅ Before Pull Request

- [ ] Pre-commit hooks ran successfully
- [ ] Security scan passed (Gitleaks, TruffleHog)
- [ ] No security findings in code review
- [ ] Documentation updated if adding new secrets/configs
- [ ] `.env.example` updated if new env vars added

---

## ✅ Before Making Repository Public

### Audit
- [ ] Run full secret scan: `gitleaks detect --source . --verbose`
- [ ] Check entire git history for leaked secrets
- [ ] Review all issues for sensitive data
- [ ] Review all closed PRs for sensitive data
- [ ] Check GitHub Security tab for vulnerabilities

### GitHub Settings
- [ ] Enable Dependabot alerts
- [ ] Enable Secret scanning
- [ ] Enable Code scanning (CodeQL)
- [ ] Enable vulnerability reporting
- [ ] Add SECURITY.md file
- [ ] Configure branch protection rules

### Documentation
- [ ] README has no sensitive information
- [ ] All docs use placeholder values only
- [ ] Setup instructions don't expose secrets
- [ ] Examples use mock/test data only

---

## ✅ Regular Maintenance (Monthly)

### Secrets Rotation
- [ ] Rotate API keys (90 days)
- [ ] Rotate database passwords (90 days)
- [ ] Rotate service account keys (90 days)
- [ ] Update GitHub secrets if rotated

### Security Updates
- [ ] Review Dependabot PRs
- [ ] Update security dependencies
- [ ] Review CodeQL findings
- [ ] Check for new CVEs in dependencies

### Monitoring
- [ ] Review GitHub security alerts
- [ ] Check for unusual access patterns
- [ ] Audit service account usage
- [ ] Review API key usage

---

## 🚨 If Secret is Leaked

### Immediate Actions
1. **Revoke the exposed secret immediately**
2. **Generate new credentials**
3. **Update in all environments (GitHub Secrets, TF Cloud, etc.)**
4. **Check logs for unauthorized access**
5. **Notify security team (if applicable)**

### Cleanup
1. **Remove secret from git history:**
   ```bash
   # Using BFG Repo-Cleaner (recommended)
   bfg --delete-files secrets.env
   
   # Or using git filter-branch
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch path/to/secret' \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (after team coordination)
   git push origin --force --all
   ```

2. **Verify removal:**
   ```bash
   gitleaks detect --source . --verbose --log-level debug
   ```

3. **Document incident**
4. **Review access logs for the leaked credential**

---

## 🔐 Secret Types to Watch For

### API Keys & Tokens
- ✅ NVIDIA NIM API keys
- ✅ GitHub Personal Access Tokens (PAT)
- ✅ Google Cloud API keys
- ✅ OAuth tokens
- ✅ JWT secrets

### Cloud Provider Credentials
- ✅ GCP service account keys (.json)
- ✅ AWS access keys (AKIA...)
- ✅ Azure connection strings

### Database & Services
- ✅ PostgreSQL passwords
- ✅ Redis connection strings
- ✅ Database URLs with credentials

### Certificates & Keys
- ✅ SSL/TLS certificates (.pem, .crt)
- ✅ Private keys (.key, id_rsa)
- ✅ SSH keys

---

## 📊 Security Tools Checklist

### Installed & Configured
- [ ] Gitleaks (secret scanning)
- [ ] TruffleHog (secret scanning)
- [ ] Pre-commit hooks
- [ ] GitHub secret scanning
- [ ] CodeQL analysis
- [ ] Dependabot
- [ ] Bandit (Python security)
- [ ] tfsec (Terraform security)

### CI/CD Checks
- [ ] Security scan runs on every PR
- [ ] Blocks merge if secrets detected
- [ ] Dependency vulnerability checks
- [ ] SAST (Static Application Security Testing)

---

## ✅ Quick Check Commands

```bash
# Scan for secrets in current code
gitleaks detect --source . --verbose

# Scan entire git history
gitleaks detect --source . --verbose --log-opts="--all"

# Check for large files that might contain secrets
find . -type f -size +100k -not -path "*/node_modules/*" -not -path "*/.git/*"

# Find files that should be in .gitignore
git status --ignored

# Check for API key patterns
grep -r "api[_-]key" . --include="*.py" --include="*.js" --include="*.ts" --include="*.tf"
grep -r "password" . --include="*.py" --include="*.js" --include="*.ts" --include="*.tf"
```

---

## 📞 Security Contacts

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. Contact the security team privately
3. Follow responsible disclosure guidelines
4. Allow reasonable time for fixes before public disclosure

---

**Last Updated:** $(date +%Y-%m-%d)
**Review Frequency:** Monthly
**Next Review:** Add 1 month from last update

