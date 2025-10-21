#!/bin/bash

# Prerequisites validation script
# Checks for required tools and provides helpful installation instructions

set -e

echo "🔍 Checking prerequisites..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        return 1
    fi
}

# Function to provide installation instructions
install_instructions() {
    case "$1" in
        "bun")
            echo -e "${YELLOW}   Install: curl -fsSL https://bun.sh/install | bash${NC}"
            ;;
        "docker")
            echo -e "${YELLOW}   Install: https://docs.docker.com/get-docker/${NC}"
            ;;
        "podman")
            echo -e "${YELLOW}   Install: brew install podman (macOS) or dnf install podman (Fedora)${NC}"
            ;;
        "helm")
            echo -e "${YELLOW}   Install: https://helm.sh/docs/intro/install/${NC}"
            ;;
        "kubectl")
            echo -e "${YELLOW}   Install: https://kubernetes.io/docs/tasks/tools/${NC}"
            ;;
    esac
}

# Check required tools
REQUIRED_TOOLS=("bun")
OPTIONAL_TOOLS=("docker" "podman" "helm" "kubectl")

echo ""
echo "📋 Required tools:"
MISSING_REQUIRED=0
for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! check_command "$tool"; then
        install_instructions "$tool"
        MISSING_REQUIRED=1
    fi
done

echo ""
echo "🔧 Optional tools (at least one container runtime required):"
CONTAINER_RUNTIME_FOUND=0
for tool in "${OPTIONAL_TOOLS[@]}"; do
    if check_command "$tool"; then
        if [[ "$tool" == "docker" || "$tool" == "podman" ]]; then
            CONTAINER_RUNTIME_FOUND=1
        fi
    else
        install_instructions "$tool"
    fi
done

echo ""
if [ $MISSING_REQUIRED -eq 1 ]; then
    echo -e "${RED}❌ Missing required tools. Please install them before proceeding.${NC}"
    exit 1
elif [ $CONTAINER_RUNTIME_FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No container runtime found. Install Docker or Podman for containerization.${NC}"
    echo -e "${YELLOW}   You can still develop with: bun run dev${NC}"
else
    echo -e "${GREEN}🎉 All prerequisites met! You're ready to build and deploy.${NC}"
fi

echo ""
echo "🚀 Quick start commands:"
echo "   Development: bun run dev"
echo "   Build:       ./scripts/build.sh"
echo "   Deploy:      ./scripts/deploy.sh"
