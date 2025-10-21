#!/bin/bash

# Unified container push script
# Automatically detects Docker or Podman and uses the available one
# Usage: ./scripts/push.sh [registry] [tag]

set -e

IMAGE_NAME="react-bun-k8s"
REGISTRY=${1:-"docker.io"}
TAG=${2:-"latest"}
FULL_TAG="${REGISTRY}/${IMAGE_NAME}:${TAG}"

# Detect available container runtime
if command -v podman &> /dev/null; then
    CONTAINER_RUNTIME="podman"
    echo "🐋 Using Podman"
elif command -v docker &> /dev/null; then
    CONTAINER_RUNTIME="docker"
    echo "🐳 Using Docker"
else
    echo "❌ Error: Neither Docker nor Podman found. Please install one of them."
    exit 1
fi

echo "📤 Pushing image to registry..."
echo "Registry: ${REGISTRY}"
echo "Image: ${FULL_TAG}"

# Tag the image for the registry
${CONTAINER_RUNTIME} tag "${IMAGE_NAME}:${TAG}" "${FULL_TAG}"

# Push the image
${CONTAINER_RUNTIME} push "${FULL_TAG}"

echo "✅ Push completed successfully!"
echo "Image available at: ${FULL_TAG}"