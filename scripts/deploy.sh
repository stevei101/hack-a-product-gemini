#!/bin/bash

# Deploy script using Helm
# Usage: ./scripts/deploy.sh [namespace] [image-tag]

set -e

NAMESPACE=${1:-"web"}
IMAGE_TAG=${2:-"latest"}
CHART_PATH="./charts/frontend"

echo "🚀 Deploying to Kubernetes with Helm..."
echo "Namespace: ${NAMESPACE}"
echo "Image tag: ${IMAGE_TAG}"

# Create namespace if it doesn't exist
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
helm upgrade --install frontend "${CHART_PATH}" \
  --namespace "${NAMESPACE}" \
  --set image.tag="${IMAGE_TAG}" \
  --wait

echo "✅ Deployment completed successfully!"
echo "Check status with: kubectl get pods -n ${NAMESPACE}"
