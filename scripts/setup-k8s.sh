#!/bin/bash

# Kubernetes setup script for Podman
# Automatically sets up a local Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}☸️  Kubernetes Setup with Podman${NC}"
echo "=================================="

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

# Function to install Kind
install_kind() {
    echo -e "${YELLOW}📦 Installing Kind...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install kind
        else
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    else
        echo -e "${RED}❌ Unsupported OS. Please install Kind manually.${NC}"
        exit 1
    fi
}

# Function to install Minikube
install_minikube() {
    echo -e "${YELLOW}📦 Installing Minikube...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install minikube
        else
            echo -e "${RED}❌ Homebrew not found. Please install Homebrew first.${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
        sudo install minikube-linux-amd64 /usr/local/bin/minikube
        rm minikube-linux-amd64
    else
        echo -e "${RED}❌ Unsupported OS. Please install Minikube manually.${NC}"
        exit 1
    fi
}

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

if ! check_command "podman"; then
    echo -e "${RED}❌ Podman not found. Please install Podman first.${NC}"
    exit 1
fi

if ! check_command "kubectl"; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check if Kind is available
if check_command "kind"; then
    KIND_AVAILABLE=true
else
    KIND_AVAILABLE=false
fi

# Check if Minikube is available
if check_command "minikube"; then
    MINIKUBE_AVAILABLE=true
else
    MINIKUBE_AVAILABLE=false
fi

echo ""
echo "🚀 Available Kubernetes options:"

# Option 1: Kind
if [ "$KIND_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Kind available${NC}"
    KIND_CHOICE="1"
elif [ "$KIND_AVAILABLE" = false ]; then
    echo -e "${YELLOW}⚠️  Kind not found${NC}"
    KIND_CHOICE="2"
fi

# Option 2: Minikube
if [ "$MINIKUBE_AVAILABLE" = true ]; then
    echo -e "${GREEN}✅ Minikube available${NC}"
    MINIKUBE_CHOICE="1"
elif [ "$MINIKUBE_AVAILABLE" = false ]; then
    echo -e "${YELLOW}⚠️  Minikube not found${NC}"
    MINIKUBE_CHOICE="2"
fi

echo ""
echo "Choose your Kubernetes setup:"
echo "1) Kind (Kubernetes in Docker) - Recommended"
echo "2) Minikube with Podman driver"
echo "3) Install Kind"
echo "4) Install Minikube"
echo "5) Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        if [ "$KIND_AVAILABLE" = true ]; then
            echo -e "${BLUE}🚀 Setting up Kind cluster...${NC}"
            kind create cluster --name react-app
            kubectl cluster-info --context kind-react-app
            echo -e "${GREEN}✅ Kind cluster 'react-app' created successfully!${NC}"
        else
            echo -e "${RED}❌ Kind not available. Please install it first.${NC}"
            exit 1
        fi
        ;;
    2)
        if [ "$MINIKUBE_AVAILABLE" = true ]; then
            echo -e "${BLUE}🚀 Setting up Minikube with Podman...${NC}"
            minikube start --driver=podman
            kubectl get nodes
            echo -e "${GREEN}✅ Minikube cluster started successfully!${NC}"
        else
            echo -e "${RED}❌ Minikube not available. Please install it first.${NC}"
            exit 1
        fi
        ;;
    3)
        install_kind
        echo -e "${GREEN}✅ Kind installed! Run this script again to create a cluster.${NC}"
        ;;
    4)
        install_minikube
        echo -e "${GREEN}✅ Minikube installed! Run this script again to start a cluster.${NC}"
        ;;
    5)
        echo -e "${YELLOW}👋 Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Kubernetes cluster is ready!${NC}"
echo ""
echo "Next steps:"
echo "1. Install Helm: https://helm.sh/docs/intro/install/"
echo "2. Deploy your app: make deploy"
echo "3. Check status: kubectl get pods -n web"
echo ""
echo "Useful commands:"
echo "  kubectl get nodes"
echo "  kubectl get pods --all-namespaces"
echo "  make helm-install"
