#!/bin/bash
#
# GCP Infrastructure Verification Script
# Verifies all deployed resources and their configurations
#
# Usage: ./verify-gcp-infrastructure.sh

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="free-project-1249"
REGION="us-central1"
CLUSTER_NAME="primary-cluster"
SA_EMAIL="gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GCP Infrastructure Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Set project
echo -e "${YELLOW}Setting project to ${PROJECT_ID}...${NC}"
gcloud config set project ${PROJECT_ID}
echo ""

# Function to check resource
check_resource() {
    local resource_name=$1
    local check_command=$2
    
    echo -e "${YELLOW}Checking ${resource_name}...${NC}"
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ ${resource_name} exists${NC}"
        return 0
    else
        echo -e "${RED}✗ ${resource_name} NOT FOUND${NC}"
        return 1
    fi
}

# 1. Verify VPC Network
echo -e "${BLUE}[1/10] VPC Network${NC}"
check_resource "VPC Network (gke-network)" \
    "gcloud compute networks describe gke-network --format='value(name)'"
gcloud compute networks describe gke-network --format="table(name,autoCreateSubnetworks,routingMode)"
echo ""

# 2. Verify Subnet
echo -e "${BLUE}[2/10] Subnet${NC}"
check_resource "Subnet (gke-subnet)" \
    "gcloud compute networks subnets describe gke-subnet --region=${REGION} --format='value(name)'"
gcloud compute networks subnets describe gke-subnet --region=${REGION} --format="table(name,ipCidrRange,region)"
echo ""

# 3. Verify GKE Cluster
echo -e "${BLUE}[3/10] GKE Cluster${NC}"
check_resource "GKE Cluster (${CLUSTER_NAME})" \
    "gcloud container clusters describe ${CLUSTER_NAME} --region=${REGION} --format='value(name)'"
gcloud container clusters describe ${CLUSTER_NAME} --region=${REGION} --format="table(name,location,status,currentMasterVersion,currentNodeCount)"
echo ""

# 4. Verify Node Pool
echo -e "${BLUE}[4/10] GKE Node Pool${NC}"
gcloud container node-pools list --cluster=${CLUSTER_NAME} --region=${REGION} --format="table(name,status,config.machineType,initialNodeCount)"
echo ""

# 5. Verify GCS Bucket
echo -e "${BLUE}[5/10] Cloud Storage Bucket${NC}"
BUCKET_NAME="${PROJECT_ID}-frontend-bucket"
check_resource "GCS Bucket (${BUCKET_NAME})" \
    "gcloud storage buckets describe gs://${BUCKET_NAME} --format='value(name)'"
gcloud storage buckets describe gs://${BUCKET_NAME} --format="table(name,location,storageClass)"
echo ""

# 6. Verify Artifact Registry
echo -e "${BLUE}[6/10] Artifact Registry${NC}"
check_resource "Artifact Registry (app-images)" \
    "gcloud artifacts repositories describe app-images --location=${REGION} --format='value(name)'"
gcloud artifacts repositories describe app-images --location=${REGION} --format="table(name,format,location)"
echo ""

# 7. Verify Service Account
echo -e "${BLUE}[7/10] Service Account${NC}"
check_resource "Service Account (gke-application-sa)" \
    "gcloud iam service-accounts describe ${SA_EMAIL} --format='value(email)'"
gcloud iam service-accounts describe ${SA_EMAIL} --format="table(email,displayName)"
echo ""

# 8. Verify IAM Bindings
echo -e "${BLUE}[8/10] IAM Bindings${NC}"
echo -e "${YELLOW}Project IAM roles for ${SA_EMAIL}:${NC}"
gcloud projects get-iam-policy ${PROJECT_ID} \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:${SA_EMAIL}" \
    --format="table(bindings.role)"
echo ""

# 9. Verify Workload Identity
echo -e "${BLUE}[9/10] Workload Identity Configuration${NC}"
echo -e "${YELLOW}Checking Workload Identity Pool...${NC}"
gcloud iam workload-identity-pools describe github-actions-pool --location=global --format="table(name,state)" 2>/dev/null || echo -e "${YELLOW}WIF Pool not found (expected if using service account keys)${NC}"
echo ""

# 10. Get kubectl credentials and verify Kubernetes
echo -e "${BLUE}[10/10] Kubernetes Resources${NC}"
echo -e "${YELLOW}Getting kubectl credentials...${NC}"
gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION}

echo -e "${YELLOW}Kubernetes Nodes:${NC}"
kubectl get nodes -o wide

echo ""
echo -e "${YELLOW}Kubernetes Service Account:${NC}"
kubectl get serviceaccount app-ksa -n default -o yaml 2>/dev/null || echo -e "${YELLOW}Service account 'app-ksa' not found in default namespace${NC}"

echo ""
echo -e "${YELLOW}Kubernetes Namespaces:${NC}"
kubectl get namespaces

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Infrastructure Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Summary
echo -e "${GREEN}✓ Network Infrastructure:${NC} VPC and Subnet configured"
echo -e "${GREEN}✓ GKE Cluster:${NC} ${CLUSTER_NAME} running in ${REGION}"
echo -e "${GREEN}✓ Storage:${NC} GCS bucket for frontend hosting"
echo -e "${GREEN}✓ Container Registry:${NC} Artifact Registry ready for images"
echo -e "${GREEN}✓ IAM:${NC} Service accounts and permissions configured"
echo -e "${GREEN}✓ Kubernetes:${NC} Cluster accessible via kubectl"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "1. Build and push Docker images:"
echo "   docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/app-images/frontend:latest ."
echo "   docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/app-images/frontend:latest"
echo ""
echo "2. Deploy applications with Helm:"
echo "   helm upgrade --install frontend ./charts/frontend"
echo ""
echo "3. Check deployment status:"
echo "   kubectl get deployments,pods,services -A"
echo ""
echo -e "${GREEN}✓ Verification complete!${NC}"

