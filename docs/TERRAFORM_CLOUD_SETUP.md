# Terraform Cloud Setup Guide

This guide will help you configure Terraform Cloud for managing your infrastructure state.

## Prerequisites

- A Terraform Cloud account (sign up at https://app.terraform.io)
- Admin access to your GitHub repository

## Step 1: Create a Terraform Cloud Organization

1. Log in to [Terraform Cloud](https://app.terraform.io)
2. Click "Create Organization" (if you don't have one already)
3. Use the organization name: **`disposable-org`**
   - This must match the organization name in `terraform/main.tf`

## Step 2: Create Workspaces

You need to create two workspaces for your environments:

### Development Workspace
1. In Terraform Cloud, click "New Workspace"
2. Choose "CLI-driven workflow"
3. Name it: **`product-mindset-dev`**
4. Click "Create workspace"
5. Go to "Settings" → "General" and add tag: `product-mindset`

### Production Workspace
1. Click "New Workspace" again
2. Choose "CLI-driven workflow"
3. Name it: **`product-mindset-prod`**
4. Click "Create workspace"
5. Go to "Settings" → "General" and add tag: `product-mindset`

## Step 3: Configure AWS Credentials in Terraform Cloud

For each workspace (dev and prod), configure AWS credentials:

1. Go to the workspace
2. Click "Variables"
3. Add the following **Environment Variables** (mark as Sensitive):
   - `AWS_ACCESS_KEY_ID` - (You can leave this empty if using OIDC)
   - `AWS_SECRET_ACCESS_KEY` - (You can leave this empty if using OIDC)

**Note**: Since your GitHub Actions workflow uses OIDC authentication with AWS, Terraform Cloud will inherit the AWS credentials from the GitHub Actions environment. The workflow configures AWS credentials before running Terraform commands.

## Step 4: Generate a Terraform Cloud API Token

1. In Terraform Cloud, click your user icon → "User Settings"
2. Click "Tokens"
3. Click "Create an API token"
4. Name it: `github-actions-product-mindset`
5. Click "Create API token"
6. **Copy the token immediately** (you won't be able to see it again)

## Step 5: Add the Token to GitHub Secrets

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `TF_API_TOKEN`
5. Value: Paste the token from Step 4
6. Click "Add secret"

## Step 6: Verify Configuration

Your configuration is now complete! The workflow will:

1. Authenticate with Terraform Cloud using the `TF_API_TOKEN`
2. Select the appropriate workspace based on the branch:
   - `develop` branch → `product-mindset-dev` workspace
   - `main` branch → `product-mindset-prod` workspace
3. Store all Terraform state in Terraform Cloud
4. Use AWS credentials from GitHub Actions OIDC authentication

## Workspace Naming Convention

- **Development**: `product-mindset-dev`
- **Production**: `product-mindset-prod`

The workspace name is automatically selected based on the branch:
- Pushing to `develop` uses the `product-mindset-dev` workspace
- Pushing to `main` uses the `product-mindset-prod` workspace

## Terraform Cloud Configuration Details

The Terraform Cloud configuration is in `terraform/main.tf`:

```hcl
terraform {
  cloud {
    organization = "disposable-org"
    
    workspaces {
      tags = ["product-mindset"]
    }
  }
}
```

## Troubleshooting

### "No valid credential sources" error
- Ensure AWS credentials are configured in the GitHub Actions workflow (OIDC authentication)
- The workflow should run the "Configure AWS credentials" step before Terraform commands

### "Organization not found" error
- Verify the organization name in `terraform/main.tf` matches your Terraform Cloud organization
- Ensure the `TF_API_TOKEN` secret is correctly set in GitHub

### "Workspace not found" error
- Create the workspace in Terraform Cloud with the exact name: `product-mindset-dev` or `product-mindset-prod`
- Ensure the workspace has the `product-mindset` tag

### "Invalid token" error
- Regenerate the API token in Terraform Cloud
- Update the `TF_API_TOKEN` secret in GitHub

## Next Steps

Once configured, every push to `develop` or `main` will:
1. Run Terraform plan
2. Apply the infrastructure changes automatically
3. Store the state in Terraform Cloud
4. Build and deploy your application

You can view the Terraform runs and state in the Terraform Cloud UI.

