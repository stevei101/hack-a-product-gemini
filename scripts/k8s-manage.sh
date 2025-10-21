#!/bin/bash
# k8s-manage.sh - Helper script for managing local Kubernetes clusters

# Function to print help message
show_help() {
    echo "Usage: ./k8s-manage.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  setup         Set up local Kubernetes cluster"
    echo "  kind          Create Kind cluster"
    echo "  minikube      Start Minikube with Podman"
    echo "  stop          Stop Kubernetes cluster"
    echo "  status        Check Kubernetes cluster status"
}

# Main script logic
case "$1" in
    setup)
        ./scripts/setup-k8s.sh
        ;;
    kind)
        kind create cluster --name react-app
        kubectl cluster-info --context kind-react-app
        ;;
    minikube)
        minikube start --driver=podman
        kubectl get nodes
        ;;
    stop)
        if command -v kind &> /dev/null; then
            kind delete cluster --name react-app
        elif command -v minikube &> /dev/null; then
            minikube stop
        else
            echo "No Kubernetes cluster found to stop"
        fi
        ;;
    status)
        kubectl cluster-info
        kubectl get nodes
        kubectl get pods --all-namespaces
        ;;
    *)
        show_help
        ;;
esac
