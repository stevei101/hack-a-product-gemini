# GitHub Actions Setup for The Product Mindset

This guide helps you set up GitHub Actions for automated deployment of your agentic application to AWS EKS and S3/CloudFront.

## 🎯 **Overview**

Your GitHub Actions workflow will:
1. **Build and test** your React frontend and Python backend
2. **Deploy infrastructure** using Terraform Cloud
3. **Deploy application** to Amazon EKS
4. **Deploy static website** to S3/CloudFront
5. **Use secure OIDC authentication** with AWS

## 🚀 **Setup Steps**

### **Step 1: Configure GitHub Repository Secrets**

Add these secrets to your GitHub repository:

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

```
AWS_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT:role/product-mindset-github-actions-dev
AWS_REGION=us-east-1
NIM_API_KEY=your_nvidia_api_key
POSTGRES_PASSWORD=your_secure_password
```

### **Step 2: Set up Terraform Cloud**

1. **Create Terraform Cloud account** at https://app.terraform.io
2. **Create new workspace** for your project
3. **Connect to your GitHub repository**
4. **Configure workspace variables**:
   ```
   github_org = "stevei101"
   github_repo = "hack-a-product"
   environment = "dev"
   ```

### **Step 3: Deploy IAM Resources**

The Terraform configuration will create:
- ✅ IAM Policy for Terraform Cloud
- ✅ IAM Role for GitHub Actions OIDC
- ✅ OIDC Provider for GitHub
- ✅ EKS Service Roles

### **Step 4: Test Deployment**

Push to `main` or `develop` branch to trigger deployment:

```bash
git add .
git commit -m "Setup GitHub Actions deployment"
git push origin develop
```

## 📋 **Workflow Details**

### **Infrastructure Job**
- Validates Terraform configuration
- Plans infrastructure changes
- Manages AWS resources

### **Build and Test Job**
- Installs dependencies (Bun, Python)
- Builds React frontend
- Tests Python backend
- Validates code quality

### **Deploy Job**
- Authenticates with AWS using OIDC
- Builds and pushes Docker images to ECR
- Deploys to Amazon EKS using Helm
- Configures environment variables

### **Static Website Job**
- Builds optimized React frontend
- Deploys to S3 bucket
- Invalidates CloudFront cache

## 🔐 **Security Features**

### **OIDC Authentication**
- No long-lived AWS credentials
- Temporary tokens for each deployment
- Scoped permissions per environment

### **Environment Separation**
- `develop` branch → `dev` environment
- `main` branch → `prod` environment
- Separate AWS resources per environment

### **Secret Management**
- Secrets stored in GitHub
- Not exposed in logs
- Rotated regularly

## 🏗️ **Architecture**

```
GitHub Repository
       ↓
GitHub Actions
       ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Terraform     │   Docker ECR    │   S3/CloudFront │
│   Cloud         │   Registry      │   Static Site   │
│                 │                 │                 │
│ Infrastructure  │ Container Images│   Frontend      │
│ Management      │                 │   Deployment    │
└─────────────────┴─────────────────┴─────────────────┘
       ↓
Amazon EKS
   ┌─────────────┐
   │   Backend   │
   │   Service   │
   └─────────────┘
```

## 📊 **Deployment Environments**

### **Development Environment**
- **Branch**: `develop`
- **EKS Cluster**: `product-mindset-dev`
- **S3 Bucket**: `product-mindset-dev-static`
- **Namespace**: `dev`

### **Production Environment**
- **Branch**: `main`
- **EKS Cluster**: `product-mindset-prod`
- **S3 Bucket**: `product-mindset-prod-static`
- **Namespace**: `prod`

## 🔧 **Customization**

### **Environment Variables**
Update in `.github/workflows/deploy.yml`:

```yaml
env:
  AWS_REGION: us-west-2
  PROJECT_NAME: product-mindset
```

### **Deployment Triggers**
Modify trigger conditions:

```yaml
on:
  push:
    branches: [ main, develop, staging ]
  pull_request:
    branches: [ main ]
```

### **Build Steps**
Add custom build steps:

```yaml
- name: Run custom tests
  run: |
    # Your custom test commands
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **AWS Authentication Failed**
   ```bash
   # Check AWS_ROLE_ARN secret is correct
   # Verify OIDC provider is configured
   # Ensure repository has correct permissions
   ```

2. **Terraform Plan Failed**
   ```bash
   # Check Terraform Cloud workspace configuration
   # Verify AWS credentials in Terraform Cloud
   # Check for resource conflicts
   ```

3. **EKS Deployment Failed**
   ```bash
   # Verify EKS cluster exists
   # Check kubectl configuration
   # Validate Helm chart syntax
   ```

4. **S3 Deployment Failed**
   ```bash
   # Check S3 bucket permissions
   # Verify CloudFront distribution exists
   # Check AWS region configuration
   ```

### **Debug Commands**

```bash
# Check GitHub Actions logs
# Go to Actions tab → Select workflow run → View logs

# Test AWS authentication locally
aws sts get-caller-identity

# Check EKS cluster status
kubectl cluster-info

# Verify S3 bucket access
aws s3 ls s3://your-bucket-name
```

## 📚 **Next Steps**

1. **Set up monitoring** with AWS CloudWatch
2. **Configure alerts** for deployment failures
3. **Add performance testing** to the workflow
4. **Set up staging environment** for testing
5. **Implement blue-green deployments**

## 🔗 **Related Documentation**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS OIDC with GitHub Actions](https://docs.github.com/en/actions/deployment/security/hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform Cloud Documentation](https://www.terraform.io/docs/cloud)
- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)

---

**Ready to deploy?** Push to your `develop` branch and watch the magic happen! 🚀
