# Security Policy

## Supported Versions

We take security seriously. This project is currently in active development.

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| develop | :white_check_mark: |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to the repository owner
2. **GitHub Security**: Use GitHub's private security vulnerability reporting feature

### What to Include

Please include the following information:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **24 hours**: Initial response acknowledging receipt
- **7 days**: Detailed analysis and remediation plan
- **30 days**: Fix implemented and released
- **90 days**: Public disclosure (coordinated with reporter)

## Security Measures

This repository implements the following security measures:

### Automated Scanning
- ✅ Gitleaks (secret detection)
- ✅ TruffleHog (verified secret detection)
- ✅ CodeQL (code analysis)
- ✅ Bandit (Python security)
- ✅ tfsec (Terraform security)
- ✅ Dependabot (dependency vulnerabilities)

### Code Protection
- ✅ Pre-commit hooks
- ✅ Branch protection rules
- ✅ Required security reviews
- ✅ Automated security testing

### Secrets Management
- ✅ GitHub Secrets for CI/CD
- ✅ Terraform Cloud for infrastructure
- ✅ Environment variables only
- ✅ No hardcoded secrets

## Best Practices

When contributing:

1. **Never** commit secrets, API keys, or credentials
2. **Always** use environment variables for sensitive data
3. **Run** pre-commit hooks before committing
4. **Review** security checklist before PRs
5. **Update** dependencies regularly

## Security Contacts

- **Repository Owner**: stevei101
- **GitHub Security**: https://github.com/stevei101/hack-a-product-gemini/security

---

Thank you for helping keep this project secure!
