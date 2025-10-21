#!/bin/bash

echo "🔍 Verifying Complete OIDC Setup"
echo "================================"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="product-mindset-github-actions-dev"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "Account ID: $ACCOUNT_ID"
echo ""

# 1. Check if OIDC provider exists
echo "🔍 Checking OIDC Provider..."
OIDC_PROVIDER_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" &>/dev/null; then
    echo "✅ OIDC Provider exists"
    
    # Get OIDC provider details
    echo "📋 OIDC Provider Details:"
    aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$OIDC_PROVIDER_ARN" --query '{URL:Url,ClientIDs:ClientIDList,Thumbprints:ThumbprintList}'
else
    echo "❌ OIDC Provider not found"
    echo "🔧 Creating OIDC Provider..."
    
    aws iam create-open-id-connect-provider \
        --url "https://token.actions.githubusercontent.com" \
        --client-id-list "sts.amazonaws.com" \
        --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
    
    if [ $? -eq 0 ]; then
        echo "✅ OIDC Provider created successfully"
    else
        echo "❌ Failed to create OIDC provider"
        exit 1
    fi
fi

echo ""

# 2. Check IAM role
echo "🔍 Checking IAM Role..."
if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
    echo "✅ IAM Role exists"
    
    # Check trust policy
    echo "📋 Trust Policy:"
    aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' --output json
    
    # Check attached policies
    echo ""
    echo "📋 Attached Policies:"
    aws iam list-attached-role-policies --role-name "$ROLE_NAME"
    
else
    echo "❌ IAM Role not found"
    exit 1
fi

echo ""

# 3. Test role assumption (this will fail but gives us useful info)
echo "🔍 Testing Role Assumption..."
echo "Note: This test will fail because we don't have a real OIDC token, but it helps verify the setup"

# Create a test trust policy to see if the role can be assumed
cat > test-trust-policy.json << EOF
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

echo "📋 Current Trust Policy vs Expected:"
echo "Expected repository: stevei101/hack-a-product"
echo "Expected ref pattern: ref:refs/heads/*"

# Get the actual trust policy and check if it matches
CURRENT_TRUST_POLICY=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.AssumeRolePolicyDocument' --output json)

# Check if the trust policy contains the correct repository
if echo "$CURRENT_TRUST_POLICY" | grep -q "stevei101/hack-a-product"; then
    echo "✅ Trust policy contains correct repository"
else
    echo "❌ Trust policy does not contain correct repository"
    echo "Current trust policy:"
    echo "$CURRENT_TRUST_POLICY"
fi

# Clean up
rm test-trust-policy.json

echo ""
echo "📋 Summary:"
echo "==========="
echo "Role ARN: $ROLE_ARN"
echo "OIDC Provider: $OIDC_PROVIDER_ARN"
echo ""
echo "🔧 GitHub Repository Configuration Required:"
echo "1. Add secret: AWS_ROLE_ARN=$ROLE_ARN"
echo "2. Repository: stevei101/hack-a-product"
echo "3. Permissions: Read and write permissions"
echo ""
echo "🚀 Next Steps:"
echo "1. Verify GitHub repository secrets"
echo "2. Check GitHub repository permissions"
echo "3. Push to trigger workflow"
