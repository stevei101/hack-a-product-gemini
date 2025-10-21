#!/bin/bash

echo "🔍 Verifying GitHub Repository Setup"
echo "===================================="

# Get repository information
REPO_URL=$(git remote get-url origin 2>/dev/null)
REPO_NAME=$(echo "$REPO_URL" | sed 's/.*github.com[:/]\([^.]*\).*/\1/')

echo "Repository URL: $REPO_URL"
echo "Repository Name: $REPO_NAME"

# Check if this matches the trust policy
EXPECTED_REPO="stevei101/hack-a-product"

if [ "$REPO_NAME" = "$EXPECTED_REPO" ]; then
    echo "✅ Repository name matches trust policy"
else
    echo "❌ Repository name mismatch!"
    echo "Expected: $EXPECTED_REPO"
    echo "Actual: $REPO_NAME"
    echo ""
    echo "🔧 Fix: Update the trust policy with the correct repository name"
fi

echo ""
echo "📋 Manual Verification Steps"
echo "============================"
echo ""
echo "1. Go to: https://github.com/$REPO_NAME/settings/secrets/actions"
echo "2. Verify these secrets exist:"
echo "   - AWS_ROLE_ARN: arn:aws:iam::874834750693:role/product-mindset-github-actions-dev"
echo "   - AWS_REGION: us-east-1"
echo "   - NIM_API_KEY: (your NVIDIA API key)"
echo "   - POSTGRES_PASSWORD: (your secure password)"
echo ""
echo "3. Go to: https://github.com/$REPO_NAME/settings/actions"
echo "4. Under 'Workflow permissions':"
echo "   - Select 'Read and write permissions'"
echo "   - Check 'Allow GitHub Actions to create and approve pull requests'"
echo ""
echo "5. Under 'Actions permissions':"
echo "   - Select 'Allow all actions and reusable workflows'"
echo ""
echo "🚀 Test Commands"
echo "==============="
echo ""
echo "After verifying the above settings, test with:"
echo ""
echo "1. Manual workflow trigger:"
echo "   - Go to: https://github.com/$REPO_NAME/actions"
echo "   - Click 'Simple AWS Test' workflow"
echo "   - Click 'Run workflow'"
echo ""
echo "2. Or push a change:"
echo "   git add ."
echo "   git commit -m 'Test AWS authentication'"
echo "   git push origin develop"

echo ""
echo "🔍 Debugging Tips"
echo "================="
echo ""
echo "If the workflow still fails:"
echo "1. Check the Actions tab for detailed error logs"
echo "2. Look for CloudTrail logs in AWS Console:"
echo "   - Go to CloudTrail → Event history"
echo "   - Filter by 'AssumeRoleWithWebIdentity'"
echo "   - Look for failed events with error details"
echo ""
echo "3. Common error patterns:"
echo "   - 'InvalidIdentityToken': Trust policy condition mismatch"
echo "   - 'AccessDenied': Role permissions issue"
echo "   - 'NoSuchEntity': Role or OIDC provider missing"
