# Kubernetes Configuration for NVIDIA NIMs

This directory contains the necessary Kubernetes configurations to deploy the NVIDIA GPU Operator and the NIM microservices.

## 1. NVIDIA GPU Operator

The NVIDIA GPU Operator is required to manage the GPU resources on the EKS nodes. It should be installed via Helm.

**Installation Steps:**

1.  Add the NVIDIA Helm repository:
    ```sh
    helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
    helm repo update
    ```

2.  Install the GPU Operator:
    ```sh
    helm install --wait --generate-name \
      -n gpu-operator --create-namespace \
      nvidia/gpu-operator
    ```

## 2. NVIDIA NIMs

The NIMs for Llama-3.1 and the embedding model will also be deployed via Helm from the NVIDIA repository. Placeholder `values.yaml` files can be created here to customize their deployments.

```