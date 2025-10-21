# Container Registry Setup Guide

This guide helps you choose and configure a container registry for The Product Mindset application.

## 🐳 **Recommended Container Registries**

### **1. GitHub Container Registry (GHCR) - RECOMMENDED**

**Best for**: GitHub users, open source projects, cost-effective solutions

**Pros**:
- ✅ Free for public repositories
- ✅ Integrated with GitHub
- ✅ Secure with GitHub authentication
- ✅ No bandwidth limits for public repos
- ✅ Easy CI/CD integration

**Setup**:
```bash
# 1. Create GitHub Personal Access Token with 'write:packages' permission
# 2. Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 3. Build and push
make container-build-registry REGISTRY=ghcr.io/YOUR_USERNAME/product-mindset
make container-push REGISTRY=ghcr.io/YOUR_USERNAME/product-mindset
```

**Example URLs**:
- `ghcr.io/your-username/product-mindset:frontend`
- `ghcr.io/your-username/product-mindset:backend`

---

### **2. Docker Hub**

**Best for**: Wide compatibility, simple setup

**Pros**:
- ✅ Most widely supported
- ✅ Free for public repositories
- ✅ Simple authentication
- ✅ Large community

**Setup**:
```bash
# 1. Create account at hub.docker.com
# 2. Login to Docker Hub
docker login

# 3. Build and push
make container-build-registry REGISTRY=YOUR_USERNAME/product-mindset
make container-push REGISTRY=YOUR_USERNAME/product-mindset
```

**Example URLs**:
- `your-username/product-mindset:frontend`
- `your-username/product-mindset:backend`

---

### **3. Amazon ECR (Elastic Container Registry)**

**Best for**: AWS deployments, enterprise security

**Pros**:
- ✅ AWS native integration
- ✅ Highly secure with IAM
- ✅ Perfect for EKS deployments
- ✅ Automatic image scanning
- ✅ Lifecycle policies

**Setup**:
```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name product-mindset --region us-west-2

# 2. Get login token
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com

# 3. Build and push
make container-build-registry REGISTRY=YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/product-mindset
make container-push REGISTRY=YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/product-mindset
```

**Example URLs**:
- `123456789.dkr.ecr.us-west-2.amazonaws.com/product-mindset:frontend`
- `123456789.dkr.ecr.us-west-2.amazonaws.com/product-mindset:backend`

---

### **4. Google Container Registry (GCR)**

**Best for**: Google Cloud deployments

**Setup**:
```bash
# 1. Configure gcloud
gcloud auth configure-docker

# 2. Build and push
make container-build-registry REGISTRY=gcr.io/YOUR_PROJECT_ID/product-mindset
make container-push REGISTRY=gcr.io/YOUR_PROJECT_ID/product-mindset
```

---

## 🏷️ **Tagging Strategy**

We use semantic tags for different environments:

```bash
# Development
product-mindset:frontend-dev
product-mindset:backend-dev

# Staging
product-mindset:frontend-staging
product-mindset:backend-staging

# Production
product-mindset:frontend
product-mindset:backend

# Versioned releases
product-mindset:frontend-v1.0.0
product-mindset:backend-v1.0.0
```

## 🚀 **Quick Start Commands**

### **Current Setup (Docker Hub)**
```bash
# Build for current Docker Hub setup
make dockerhub-build

# Push to current Docker Hub setup
make dockerhub-push
```

### **Future GHCR Setup**
```bash
# Build for GHCR (when ready to migrate)
make ghcr-build USERNAME=your-username

# Push to GHCR (when ready to migrate)
make ghcr-push USERNAME=your-username
```

### **Generic Registry Commands**
```bash
# Build with any registry
make container-build-registry REGISTRY=your-registry/image-name

# Push to any registry
make container-push REGISTRY=your-registry/image-name
```

### **Deploy with Helm**
```bash
# Update Helm values.yaml with your registry
# Then deploy
make helm-upgrade
```

## 📝 **Configuration Examples**

### **For GitHub Container Registry**
```yaml
# charts/frontend/values.yaml
image:
  repository: ghcr.io/your-username/product-mindset
  tag: frontend

# charts/backend/values.yaml  
image:
  repository: ghcr.io/your-username/product-mindset
  tag: backend
```

### **For Docker Hub (Current Setup)**
```yaml
# charts/frontend/values.yaml
image:
  repository: smithveunsa/react-bun-k8s
  tag: frontend

# charts/backend/values.yaml
image:
  repository: smithveunsa/react-bun-k8s
  tag: backend
```

### **For Docker Hub (Generic)**
```yaml
# charts/frontend/values.yaml
image:
  repository: your-username/product-mindset
  tag: frontend

# charts/backend/values.yaml
image:
  repository: your-username/product-mindset
  tag: backend
```

### **For Amazon ECR**
```yaml
# charts/frontend/values.yaml
image:
  repository: 123456789.dkr.ecr.us-west-2.amazonaws.com/product-mindset
  tag: frontend

# charts/backend/values.yaml
image:
  repository: 123456789.dkr.ecr.us-west-2.amazonaws.com/product-mindset
  tag: backend
```

## 🔐 **Authentication Setup**

### **GitHub Container Registry**
```bash
# Create Personal Access Token with 'write:packages' permission
export GITHUB_TOKEN=your_token_here
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### **Docker Hub**
```bash
docker login
# Enter your Docker Hub username and password
```

### **Amazon ECR**
```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com
```

## 🚀 **CI/CD Integration**

### **GitHub Actions Example**
```yaml
name: Build and Push
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to GHCR
        uses: docker/login-action@v1
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and Push
        run: |
          make container-build-registry REGISTRY=ghcr.io/${{ github.actor }}/product-mindset
          make container-push REGISTRY=ghcr.io/${{ github.actor }}/product-mindset
```

## 📊 **Registry Comparison**

| Feature | GHCR | Docker Hub | ECR | GCR |
|---------|------|------------|-----|-----|
| **Free Tier** | ✅ Public repos | ✅ Public repos | ❌ Pay per GB | ❌ Pay per GB |
| **Private Repos** | ✅ Free | ❌ Limited | ✅ Pay per repo | ✅ Pay per repo |
| **AWS Integration** | ❌ | ❌ | ✅ Native | ❌ |
| **GitHub Integration** | ✅ Native | ❌ | ❌ | ❌ |
| **Security Scanning** | ✅ | ✅ | ✅ | ✅ |
| **Bandwidth Limits** | ❌ | ✅ Limited | ✅ | ✅ |

## 🎯 **Recommendation**

**For your hackathon project, I recommend GitHub Container Registry (GHCR)** because:

1. **Free** for public repositories
2. **Integrated** with GitHub (if you're using GitHub)
3. **Secure** and reliable
4. **Easy setup** with GitHub tokens
5. **No bandwidth limits** for public repos
6. **Perfect** for hackathon demonstrations

## 🚀 **Next Steps**

1. **Choose your registry** (recommended: GHCR)
2. **Set up authentication**
3. **Build and push your images**:
   ```bash
   make container-build-registry REGISTRY=your-registry/product-mindset
   make container-push REGISTRY=your-registry/product-mindset
   ```
4. **Update Helm values** with your registry
5. **Deploy to Kubernetes**

---

**Need help?** Check the [Kubernetes Deployment Guide](README.md#kubernetes-deployment) or run `make help` for all available commands.
