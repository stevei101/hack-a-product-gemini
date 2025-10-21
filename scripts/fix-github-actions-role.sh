#!/bin/bash

echo "🔧 Fixing GitHub Actions IAM Role Permissions"
echo "=============================================="

# Get current AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="product-mindset-github-actions-dev"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

echo "Account ID: $ACCOUNT_ID"
echo "Role Name: $ROLE_NAME"

# Create the GitHub Actions policy
echo ""
echo "📝 Creating GitHub Actions IAM Policy..."

cat > github-actions-policy.json << EOF
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
                "arn:aws:s3:::product-mindset-*",
                "arn:aws:s3:::product-mindset-*/*"
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
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
POLICY_NAME="${ROLE_NAME}-policy"
aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file://github-actions-policy.json \
    --description "Policy for GitHub Actions deployment"

if [ $? -eq 0 ]; then
    echo "✅ Policy created successfully: $POLICY_NAME"
else
    echo "⚠️  Policy might already exist, continuing..."
fi

# Attach the policy to the role
echo ""
echo "🔗 Attaching policy to role..."
aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

if [ $? -eq 0 ]; then
    echo "✅ Policy attached successfully"
else
    echo "❌ Failed to attach policy"
fi

# Verify the role configuration
echo ""
echo "🔍 Verifying role configuration..."
aws iam get-role --role-name "$ROLE_NAME" --query 'Role.{RoleName:RoleName,Arn:Arn,CreateDate:CreateDate}'

echo ""
echo "📋 Attached policies:"
aws iam list-attached-role-policies --role-name "$ROLE_NAME"

# Clean up
rm github-actions-policy.json

echo ""
echo "✅ GitHub Actions role setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Make sure your GitHub repository secret is set:"
echo "   AWS_ROLE_ARN=$ROLE_ARN"
echo ""
echo "2. Check GitHub repository settings:"
echo "   - Settings → Actions → General → Workflow permissions: 'Read and write permissions'"
echo "   - Settings → Actions → General → Allow GitHub Actions to create and approve pull requests: Checked"
echo ""
echo "3. Push to trigger the workflow and test the deployment"
