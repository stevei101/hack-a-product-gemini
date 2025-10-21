# AWS Permissions Setup for The Product Mindset

This guide helps you set up the necessary AWS IAM permissions for Terraform Cloud and GitHub Actions to deploy your agentic application.

## 🎯 **Overview**

Your plan is **valid and follows AWS security best practices**. We'll implement:

1. **IAM Policy for Terraform Cloud User** - Infrastructure management
2. **IAM Role for GitHub Actions OIDC** - Application deployment
3. **EKS Service Roles** - For your agentic application
4. **Proper Resource Scoping** - Least privilege access

## 🚀 **Quick Start for GitHub Actions**

### **Step 1: Deploy IAM Resources with Terraform Cloud**

Since you're using GitHub Actions, deploy the IAM resources through Terraform Cloud:

1. **Create Terraform Cloud workspace** for your project
2. **Upload the terraform configuration** to your repository
3. **Configure Terraform Cloud variables**:
   ```
   github_org = "stevei101"
   github_repo = "hack-a-product"
   environment = "dev"
   ```

### **Step 2: Configure GitHub Actions Secrets**

Add these secrets to your GitHub repository:

```
AWS_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT:role/product-mindset-github-actions-dev
AWS_REGION=us-east-1
NIM_API_KEY=your_nvidia_api_key
POSTGRES_PASSWORD=your_secure_password
```

### **Step 3: Deploy with GitHub Actions**

The deployment will happen automatically when you push to `main` or `develop` branches:

1. **Infrastructure** - Managed by Terraform Cloud
2. **Application** - Deployed by GitHub Actions to EKS
3. **Static Website** - Deployed to S3/CloudFront

## 📋 **Detailed Setup Instructions**

### **1. Terraform Cloud IAM User Setup**

The Terraform Cloud user needs broad permissions to create infrastructure:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutBucketWebsite", 
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:DeleteBucket",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::product-mindset-*",
        "arn:aws:s3:::product-mindset-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:UpdateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:DeleteDistribution",
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:DeleteOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:UpdateOriginAccessControl",
        "cloudfront:ListDistributions",
        "cloudfront:GetDistributionConfig"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:CreateCluster",
        "eks:DeleteCluster",
        "eks:DescribeCluster",
        "eks:UpdateClusterConfig",
        "eks:TagResource",
        "eks:UntagResource",
        "eks:ListClusters"
      ],
      "Resource": "*"
    }
  ]
}
```

### **2. GitHub Actions OIDC Setup**

The GitHub Actions role uses OIDC for secure, keyless authentication:

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:stevei101/hack-a-product:ref:refs/heads/dev"
        }
      }
    }
  ]
}
```

**Permissions Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::product-mindset-dev-*",
        "arn:aws:s3:::product-mindset-dev-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:AccessKubernetesApi"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🔧 **Environment-Specific Configuration**

### **Development Environment**
```bash
environment = "dev"
github_repo = "hack-a-product"
```

### **Production Environment**
```bash
environment = "prod"  
github_repo = "hack-a-product"
# Update the OIDC condition to use "refs/heads/main"
```

## 🧪 **Testing the Setup**

### **Test Terraform Cloud Permissions**
```bash
# In your Terraform Cloud workspace
terraform plan
# Should successfully plan infrastructure creation
```

### **Test GitHub Actions Permissions**
```bash
# Trigger a deployment in GitHub Actions
# Should successfully assume role and deploy
```

### **Test EKS Permissions**
```bash
# Deploy your agentic application
kubectl apply -f charts/
# Should successfully deploy to EKS
```

## 📊 **Resource Naming Convention**

Based on your existing patterns, resources will be named:
- IAM Policies: `product-mindset-{purpose}-{environment}`
- IAM Roles: `product-mindset-{purpose}-{environment}`
- S3 Buckets: `product-mindset-{environment}-{purpose}`
- EKS Cluster: `product-mindset-{environment}`

## 🔐 **Security Best Practices**

1. **Principle of Least Privilege** - Each role has only necessary permissions
2. **Resource Scoping** - Policies scoped to specific resources
3. **OIDC Authentication** - No long-lived credentials for GitHub Actions
4. **Environment Separation** - Different roles for dev/staging/prod
5. **Audit Logging** - CloudTrail enabled for all actions

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **OIDC Provider Not Found**
   ```bash
   # Ensure OIDC provider is created first
   terraform apply -target=aws_iam_openid_connect_provider.github
   ```

2. **GitHub Actions Can't Assume Role**
   ```bash
   # Check the repository name and branch in OIDC condition
   # Verify AWS_ROLE_ARN secret is correct
   ```

3. **Terraform Cloud Permission Denied**
   ```bash
   # Ensure IAM policy is attached to the correct user
   # Verify AWS credentials in Terraform Cloud workspace
   ```

## 📚 **Next Steps**

1. **Deploy IAM resources** using the Terraform configuration
2. **Configure Terraform Cloud** with the IAM policy
3. **Set up GitHub Actions** with OIDC authentication
4. **Test the deployment** pipeline
5. **Deploy your agentic application** to EKS

## 🔗 **Related Documentation**

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security/hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [EKS IAM Roles](https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html)

---

**Need help?** Check the [Terraform documentation](terraform/) or run `terraform plan` to validate your configuration.
