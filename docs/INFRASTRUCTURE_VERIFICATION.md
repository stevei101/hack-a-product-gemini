# 🔍 GCP Infrastructure Verification Guide

Complete guide to verify all deployed resources in Google Cloud Platform.

---

## 🚀 Quick Verification (Automated)

Run the automated verification script:

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Optional: customize other settings
export GCP_REGION="us-central1"
export CLUSTER_NAME="primary-cluster"

# Run verification
cd scripts
./verify-gcp-infrastructure.sh
```

This will check all 10 infrastructure components and provide a summary.

---

## 📋 Manual Verification Steps

### **Prerequisites**

```bash
# Set your project (REPLACE WITH YOUR ACTUAL PROJECT ID)
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Configure gcloud
gcloud config set project ${GCP_PROJECT_ID}
```

---

## 1️⃣ VPC Network

### **CLI Verification:**
```bash
# List networks
gcloud compute networks list

# Describe the GKE network
gcloud compute networks describe gke-network
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/networking/networks/list
- Look for: **gke-network**
- Status: ✅ Should show "ACTIVE"

### **Expected:**
- Network: `gke-network`
- Auto-create subnets: `false` (custom mode)
- Routing mode: `REGIONAL` or `GLOBAL`

---

## 2️⃣ Subnet

### **CLI Verification:**
```bash
# List subnets
gcloud compute networks subnets list --network=gke-network

# Describe the subnet
gcloud compute networks subnets describe gke-subnet --region=${REGION}
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/networking/networks/list
- Click on **gke-network** → **SUBNETS** tab
- Look for: **gke-subnet**

### **Expected:**
- Name: `gke-subnet`
- Region: `us-central1`
- IP range: `10.10.0.0/24`
- Network: `gke-network`

---

## 3️⃣ GKE Cluster

### **CLI Verification:**
```bash
# List clusters
gcloud container clusters list

# Describe the cluster
gcloud container clusters describe primary-cluster --region=${REGION}

# Check cluster status
gcloud container clusters describe primary-cluster \
  --region=${REGION} \
  --format="value(status)"
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/kubernetes/list
- Look for: **primary-cluster**
- Status: ✅ Should show "RUNNING" (green checkmark)

### **Expected:**
- Name: `primary-cluster`
- Location: `us-central1` (regional)
- Status: `RUNNING`
- Nodes: 1 or more
- Workload Identity: ENABLED

---

## 4️⃣ GKE Node Pool

### **CLI Verification:**
```bash
# List node pools
gcloud container node-pools list \
  --cluster=primary-cluster \
  --region=${REGION}

# Describe node pool
gcloud container node-pools describe primary-node-pool \
  --cluster=primary-cluster \
  --region=${REGION}
```

### **Console Verification:**
- Go to cluster details → **NODES** tab
- Look for: **primary-node-pool**

### **Expected:**
- Name: `primary-node-pool`
- Machine type: `e2-medium`
- Node count: 1
- Preemptible: `true`
- Status: `RUNNING`

---

## 5️⃣ Cloud Storage Bucket

### **CLI Verification:**
```bash
# List buckets
gcloud storage buckets list

# Describe bucket
gcloud storage buckets describe gs://${PROJECT_ID}-frontend-bucket

# Check bucket contents
gcloud storage ls gs://${PROJECT_ID}-frontend-bucket/
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/storage/browser
- Look for: **[PROJECT_ID]-frontend-bucket**

### **Expected:**
- Name: `[PROJECT_ID]-frontend-bucket`
- Location: `US` (multi-region)
- Storage class: `STANDARD`
- Public access: `Not public` (uniform bucket-level access)
- Website configuration: `index.html`

---

## 6️⃣ Artifact Registry

### **CLI Verification:**
```bash
# List repositories
gcloud artifacts repositories list --location=${REGION}

# Describe repository
gcloud artifacts repositories describe app-images --location=${REGION}

# List images (will be empty until you push)
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/app-images
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/artifacts
- Look for: **app-images**
- Location: `us-central1`

### **Expected:**
- Repository: `app-images`
- Format: `DOCKER`
- Location: `us-central1`
- Status: `Ready`

---

## 7️⃣ Service Accounts

### **CLI Verification:**
```bash
# List service accounts
gcloud iam service-accounts list

# Describe GKE application service account
gcloud iam service-accounts describe gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Describe GitHub Actions runner SA
gcloud iam service-accounts describe github-actions-runner@${PROJECT_ID}.iam.gserviceaccount.com
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=[YOUR_PROJECT_ID]
- Look for:
  - **gke-application-sa** (for GKE workloads)
  - **github-actions-runner** (for CI/CD)

### **Expected Service Accounts:**
1. `gke-application-sa@[PROJECT_ID].iam.gserviceaccount.com`
   - Display name: "GKE Application Service Account"
2. `github-actions-runner@[PROJECT_ID].iam.gserviceaccount.com`
   - Display name: "GitHub Actions Runner"

---

## 8️⃣ IAM Permissions

### **CLI Verification:**
```bash
# Check project IAM policy for gke-application-sa
gcloud projects get-iam-policy ${PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --format="table(bindings.role)"

# Check service account IAM policy (Workload Identity binding)
gcloud iam service-accounts get-iam-policy \
  gke-application-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/iam-admin/iam
- Search for: `gke-application-sa`

### **Expected Permissions:**

**gke-application-sa:**
- `roles/storage.objectViewer` (for GCS access)
- `roles/iam.workloadIdentityUser` (for Workload Identity)

**github-actions-runner:**
- `roles/owner` (or specific roles for deployment)
- `roles/iam.serviceAccountAdmin`
- `roles/resourcemanager.projectIamAdmin`

---

## 9️⃣ Workload Identity Federation

### **CLI Verification:**
```bash
# List Workload Identity Pools
gcloud iam workload-identity-pools list --location=global

# Describe the pool
gcloud iam workload-identity-pools describe github-actions-pool --location=global

# List providers
gcloud iam workload-identity-pools providers list \
  --workload-identity-pool=github-actions-pool \
  --location=global

# Describe provider
gcloud iam workload-identity-pools providers describe github-actions-provider \
  --workload-identity-pool=github-actions-pool \
  --location=global
```

### **Console Verification:**
- Go to: https://console.cloud.google.com/iam-admin/workload-identity-pools
- Look for: **github-actions-pool**

### **Expected:**
- Pool: `github-actions-pool`
- Provider: `github-actions-provider`
- Provider type: `OIDC`
- Issuer: `https://token.actions.githubusercontent.com`
- Attribute condition: `attribute.repository == 'stevei101/hack-a-product-gemini'`

---

## 🔟 Kubernetes Resources

### **Get kubectl Access:**
```bash
# Get credentials
gcloud container clusters get-credentials primary-cluster --region=${REGION}

# Verify connection
kubectl cluster-info
```

### **Verify Nodes:**
```bash
# List nodes
kubectl get nodes

# Describe a node (replace <node-name> with actual node name)
kubectl describe node <node-name>
```

### **Verify Kubernetes Service Account:**
```bash
# List service accounts
kubectl get serviceaccount -n default

# Describe app-ksa
kubectl get serviceaccount app-ksa -n default -o yaml

# Check annotations (should have Workload Identity annotation)
kubectl get serviceaccount app-ksa -n default -o jsonpath='{.metadata.annotations}'
```

### **Expected:**
- Nodes: 1 or more, status `Ready`
- Service account: `app-ksa` in `default` namespace
- Annotation: `iam.gke.io/gcp-service-account: gke-application-sa@PROJECT_ID.iam.gserviceaccount.com`

---

## 🧪 Test Workload Identity

Deploy a test pod to verify Workload Identity works:

```bash
# Create test pod
kubectl run test-pod --image=google/cloud-sdk:slim \
  --serviceaccount=app-ksa \
  --command -- sleep infinity

# Wait for pod to start
kubectl wait --for=condition=ready pod/test-pod --timeout=60s

# Test GCP access from pod
kubectl exec test-pod -- gcloud auth list

# Test GCS access
kubectl exec test-pod -- gcloud storage ls gs://${PROJECT_ID}-frontend-bucket

# Cleanup
kubectl delete pod test-pod
```

### **Expected:**
- Pod should start successfully
- `gcloud auth list` should show `gke-application-sa@...`
- Should be able to list GCS bucket contents

---

## 📊 Complete Infrastructure Checklist

Use this checklist to verify all components:

- [ ] **VPC Network** (`gke-network`) - Active
- [ ] **Subnet** (`gke-subnet`) - IP range 10.10.0.0/24
- [ ] **GKE Cluster** (`primary-cluster`) - Running
- [ ] **Node Pool** (`primary-node-pool`) - 1+ nodes
- [ ] **GCS Bucket** (`*-frontend-bucket`) - Created
- [ ] **Artifact Registry** (`app-images`) - Ready
- [ ] **Service Account** (`gke-application-sa`) - Created
- [ ] **IAM Bindings** - Storage viewer role assigned
- [ ] **Workload Identity** - Pool and provider configured
- [ ] **Kubernetes SA** (`app-ksa`) - Created with annotations
- [ ] **kubectl Access** - Can connect to cluster
- [ ] **Node Status** - All nodes Ready
- [ ] **WIF Test** - Pod can access GCP services

---

## 🔧 Troubleshooting

### **Issue: Cannot connect to cluster**

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Reset kubectl credentials
gcloud container clusters get-credentials primary-cluster \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID}

# Test connection
kubectl get nodes
```

### **Issue: Workload Identity not working**

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Check service account annotation
kubectl get sa app-ksa -n default -o yaml

# Verify IAM binding
gcloud iam service-accounts get-iam-policy \
  gke-application-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

### **Issue: Missing resources**

```bash
# Check Terraform state
terraform state list

# Check specific resource
terraform state show google_container_cluster.primary
```

---

## 📈 Resource Costs

Estimated monthly costs for this infrastructure:

| Resource | Type | Estimated Cost |
|----------|------|----------------|
| GKE Cluster | Regional, 1 node | ~$73/month |
| Compute (e2-medium) | Preemptible | ~$12/month |
| Network egress | Minimal | ~$1/month |
| GCS Storage | Standard | ~$0.02/GB/month |
| Artifact Registry | Storage | ~$0.10/GB/month |
| **Total** | | **~$86/month** |

*Note: Costs vary based on usage. Preemptible nodes significantly reduce costs.*

---

## 🎯 Next Steps

After verifying infrastructure:

1. **Build Docker Images**
   ```bash
   export GCP_PROJECT_ID="your-project-id"
   export GCP_REGION="us-central1"
   
   docker build -t ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/app-images/frontend:latest .
   docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/app-images/frontend:latest
   ```

2. **Deploy with Helm**
   ```bash
   helm upgrade --install frontend ./charts/frontend
   ```

3. **Deploy Static Site to GCS**
   ```bash
   gcloud storage rsync -r ./dist gs://${GCP_PROJECT_ID}-frontend-bucket
   ```

4. **Monitor Deployments**
   ```bash
   kubectl get all -A
   ```

---

## 📚 Additional Resources

- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Workload Identity Guide](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [GCS Website Hosting](https://cloud.google.com/storage/docs/hosting-static-website)
- [Artifact Registry Guide](https://cloud.google.com/artifact-registry/docs)

---

**Last Updated:** October 22, 2025  
**Status:** ✅ Ready for Application Deployment

