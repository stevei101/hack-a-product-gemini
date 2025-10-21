#!/bin/bash

echo "🐳 Creating ECR Repositories"
echo "============================"

REGION="us-east-1"
PROJECT_NAME="product-mindset"

echo "Region: $REGION"
echo "Project: $PROJECT_NAME"
echo ""

# Create frontend repository
echo "📦 Creating frontend repository..."
aws ecr create-repository \
    --repository-name "${PROJECT_NAME}-frontend" \
    --region "$REGION" \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Frontend repository created: ${PROJECT_NAME}-frontend"
else
    echo "⚠️  Frontend repository might already exist (this is ok)"
fi

# Create backend repository
echo ""
echo "📦 Creating backend repository..."
aws ecr create-repository \
    --repository-name "${PROJECT_NAME}-backend" \
    --region "$REGION" \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Backend repository created: ${PROJECT_NAME}-backend"
else
    echo "⚠️  Backend repository might already exist (this is ok)"
fi

# List all ECR repositories
echo ""
echo "📋 ECR Repositories:"
aws ecr describe-repositories --region "$REGION" --query 'repositories[*].[repositoryName,repositoryUri]' --output table

echo ""
echo "✅ ECR setup complete!"
echo ""
echo "📝 Repository URIs:"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Frontend: ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT_NAME}-frontend"
echo "Backend:  ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT_NAME}-backend"
