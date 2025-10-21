#!/bin/bash

echo "🔍 AWS OIDC Troubleshooting Script"
echo "=================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

echo "✅ AWS CLI is installed"

# Get current AWS account ID
echo ""
echo "📋 Current AWS Configuration:"
echo "Account ID: $(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo 'Not configured')"
echo "Region: $(aws configure get region 2>/dev/null || echo 'Not configured')"

# Check if IAM role exists
echo ""
echo "🔍 Checking IAM Role Configuration..."

# You'll need to replace these with your actual values
ROLE_NAME="product-mindset-github-actions-dev"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)

if [ -z "$ACCOUNT_ID" ]; then
    echo "❌ Cannot get AWS account ID. Please configure AWS credentials."
    exit 1
fi

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "Looking for role: $ROLE_ARN"

# Check if role exists
if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
    echo "✅ IAM Role exists: $ROLE_NAME"
    
    # Get trust policy
    echo ""
    echo "📄 Trust Policy:"
    aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' --output json
    
    # Check OIDC provider
    echo ""
    echo "🔍 Checking OIDC Provider..."
    if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com" &>/dev/null; then
        echo "✅ OIDC Provider exists"
    else
        echo "❌ OIDC Provider not found"
        echo "Creating OIDC provider..."
        
        # Create OIDC provider
        aws iam create-open-id-connect-provider \
            --url "https://token.actions.githubusercontent.com" \
            --client-id-list "sts.amazonaws.com" \
            --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
        
        if [ $? -eq 0 ]; then
            echo "✅ OIDC Provider created successfully"
        else
            echo "❌ Failed to create OIDC provider"
        fi
    fi
else
    echo "❌ IAM Role not found: $ROLE_NAME"
    echo ""
    echo "🔧 Creating IAM Role and Trust Policy..."
    
    # Create trust policy
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
    
    # Create role
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document file://trust-policy.json \
        --description "GitHub Actions role for The Product Mindset"
    
    if [ $? -eq 0 ]; then
        echo "✅ IAM Role created successfully"
        
        # Clean up
        rm trust-policy.json
    else
        echo "❌ Failed to create IAM Role"
        rm trust-policy.json
        exit 1
    fi
fi

echo ""
echo "📋 GitHub Repository Configuration:"
echo "Repository: stevei101/hack-a-product"
echo "Role ARN: $ROLE_ARN"
echo ""
echo "🔧 Next Steps:"
echo "1. Add this secret to your GitHub repository:"
echo "   AWS_ROLE_ARN=$ROLE_ARN"
echo ""
echo "2. Make sure your GitHub repository has the following settings:"
echo "   - Actions → General → Workflow permissions: 'Read and write permissions'"
echo "   - Actions → General → Allow GitHub Actions to create and approve pull requests: Checked"
echo ""
echo "3. Push to your repository to trigger the workflow"
