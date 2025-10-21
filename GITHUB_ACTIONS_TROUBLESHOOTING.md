# GitHub Actions AWS OIDC Troubleshooting Guide

This guide helps you fix the "Credentials could not be loaded" error in GitHub Actions.

## 🔍 **Common Causes & Solutions**

### **1. Missing or Incorrect AWS_ROLE_ARN Secret**

**Error**: `Could not load credentials from any providers`

**Solution**:
1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Check if `AWS_ROLE_ARN` secret exists
3. Verify the ARN format: `arn:aws:iam::YOUR_ACCOUNT_ID:role/product-mindset-github-actions-dev`

**How to get your Account ID**:
```bash
aws sts get-caller-identity --query Account --output text
```

### **2. IAM Role Trust Policy Issues**

**Problem**: The trust policy doesn't allow your repository to assume the role.

**Solution**: Update the trust policy to include your exact repository:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:stevei101/hack-a-product:ref:refs/heads/*"
                }
            }
        }
    ]
}
```

### **3. OIDC Provider Not Configured**

**Problem**: The GitHub OIDC provider doesn't exist in AWS.

**Solution**: Create the OIDC provider:

```bash
aws iam create-open-id-connect-provider \
    --url "https://token.actions.githubusercontent.com" \
    --client-id-list "sts.amazonaws.com" \
    --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
```

### **4. GitHub Repository Permissions**

**Problem**: GitHub Actions doesn't have permission to generate OIDC tokens.

**Solution**: 
1. Go to repository → **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select **"Read and write permissions"**
3. Check **"Allow GitHub Actions to create and approve pull requests"**

### **5. Branch/Ref Mismatch**

**Problem**: The trust policy condition doesn't match your branch.

**Current Trust Policy Condition**:
```json
"StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:stevei101/hack-a-product:ref:refs/heads/*"
}
```

**This allows**: Any branch in your repository

## 🛠️ **Automated Troubleshooting**

Run the troubleshooting script:

```bash
./scripts/troubleshoot-aws-oidc.sh
```

This script will:
- ✅ Check AWS CLI configuration
- ✅ Verify IAM role exists
- ✅ Check OIDC provider
- ✅ Create missing resources
- ✅ Provide exact configuration values

## 🔧 **Manual Verification Steps**

### **Step 1: Verify GitHub Secrets**

```bash
# Check if secrets are properly configured in GitHub
# Go to: Settings → Secrets and variables → Actions
# Required secrets:
# - AWS_ROLE_ARN
# - AWS_REGION
# - NIM_API_KEY
# - POSTGRES_PASSWORD
```

### **Step 2: Verify IAM Role**

```bash
# Check if the role exists
aws iam get-role --role-name product-mindset-github-actions-dev

# Check the trust policy
aws iam get-role --role-name product-mindset-github-actions-dev --query 'Role.AssumeRolePolicyDocument'
```

### **Step 3: Verify OIDC Provider**

```bash
# Check if OIDC provider exists
aws iam get-open-id-connect-provider --open-id-connect-provider-arn "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
```

### **Step 4: Test Role Assumption**

```bash
# Test if you can assume the role (replace with your actual role ARN)
aws sts assume-role-with-web-identity \
    --role-arn "arn:aws:iam::YOUR_ACCOUNT_ID:role/product-mindset-github-actions-dev" \
    --role-session-name "test-session" \
    --web-identity-token "dummy-token"
```

## 📋 **Complete Setup Checklist**

- [ ] **AWS CLI configured** with valid credentials
- [ ] **GitHub repository** has Actions enabled
- [ ] **GitHub secrets** configured:
  - [ ] `AWS_ROLE_ARN`
  - [ ] `AWS_REGION`
  - [ ] `NIM_API_KEY`
  - [ ] `POSTGRES_PASSWORD`
- [ ] **OIDC provider** created in AWS IAM
- [ ] **IAM role** created with correct trust policy
- [ ] **GitHub repository permissions** allow Actions
- [ ] **Branch/ref conditions** match your workflow

## 🚨 **Quick Fix Commands**

If you need to recreate everything:

```bash
# 1. Create OIDC provider
aws iam create-open-id-connect-provider \
    --url "https://token.actions.githubusercontent.com" \
    --client-id-list "sts.amazonaws.com" \
    --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" "1c58a3a8518e8759bf075b76b750d4f2df264fcd"

# 2. Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 3. Create trust policy file
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                },
                "StringLike": {
                    "token.actions.githubusercontent.com:sub": "repo:stevei101/hack-a-product:ref:refs/heads/*"
                }
            }
        }
    ]
}
EOF

# 4. Create IAM role
aws iam create-role \
    --role-name product-mindset-github-actions-dev \
    --assume-role-policy-document file://trust-policy.json

# 5. Clean up
rm trust-policy.json

# 6. Add secret to GitHub repository:
# AWS_ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/product-mindset-github-actions-dev
```

## 📞 **Still Having Issues?**

1. **Check the GitHub Actions logs** for detailed error messages
2. **Verify your AWS account** has the necessary permissions
3. **Test the workflow** with a simple AWS CLI command first
4. **Check CloudTrail logs** for failed AssumeRoleWithWebIdentity calls

## 🔗 **Related Documentation**

- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security/hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC Identity Providers](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub Actions Permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
