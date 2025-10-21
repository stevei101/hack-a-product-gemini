#!/bin/bash

# Unified container build script
# Automatically detects Docker or Podman and uses the available one
# Usage: ./scripts/build.sh [tag] [registry]

set -e

IMAGE_NAME="react-bun-k8s"
TAG=${1:-"latest"}
REGISTRY=${2:-""}
FULL_TAG="${IMAGE_NAME}:${TAG}"

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

echo "🔨 Building image with ${CONTAINER_RUNTIME}..."
echo "Image: ${FULL_TAG}"

# Build the image
${CONTAINER_RUNTIME} build -t "${FULL_TAG}" .

echo "✅ Build completed successfully!"
echo "Run with: ${CONTAINER_RUNTIME} run -p 8080:80 ${FULL_TAG}"

# If registry is provided, tag and show push command
if [ -n "${REGISTRY}" ]; then
    REGISTRY_TAG="${REGISTRY}/${FULL_TAG}"
    echo "📤 Tagging for registry: ${REGISTRY_TAG}"
    ${CONTAINER_RUNTIME} tag "${FULL_TAG}" "${REGISTRY_TAG}"
    echo "Push with: ${CONTAINER_RUNTIME} push ${REGISTRY_TAG}"
fi