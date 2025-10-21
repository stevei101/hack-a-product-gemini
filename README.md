# The Product Mindset - Agentic Application

**The Product Mindset** is an AI-powered agentic workspace that acts as a thinking companion for creators and developers. Built for the AWS & NVIDIA Hackathon, it demonstrates cutting-edge AI integration with a focus on agentic workflows and retrieval-augmented generation.

![Screenshot of the application UI](./preview.png)

## 🎯 Hackathon Requirements

This application meets all AWS & NVIDIA Hackathon requirements:

- ✅ **NVIDIA NIM Integration**: Uses `nvidia/llama-3_1-nemotron-nano-8b-v1` for reasoning
- ✅ **Retrieval Embedding NIM**: Uses `nvidia/nv-embedqa-e5-v5` for semantic search
- ✅ **Agentic Application**: Implements perception, reasoning, and action capabilities
- ✅ **RAG Pipeline**: Complete retrieval-augmented generation system
- ✅ **Product Mindset**: AI-powered workspace for creators and developers

## 🏗️ Architecture

| Component    | Technology           | Purpose                                      |
| ------------ | -------------------- | -------------------------------------------- |
| Frontend     | **React + TypeScript** | Modern UI for agentic workflows              |
| Backend      | **Python FastAPI**   | High-performance API with async support      |
| AI/ML        | **NVIDIA NIM**       | Llama 3.1 Nemotron Nano 8B + Embeddings     |
| Database     | **PostgreSQL**       | Persistent storage for agents and tasks      |
| Cache        | **Redis**            | High-speed caching and session storage       |
| Deployment   | **Docker + K8s**     | Containerized, scalable deployment           |

## ✨ Key Features

### 🤖 Agentic AI Capabilities
- **Intelligent Reasoning**: Uses NVIDIA Llama 3.1 Nemotron Nano 8B for complex reasoning tasks
- **Semantic Search**: RAG-powered context retrieval using NVIDIA embeddings
- **Memory Management**: Persistent agent memory and project context
- **Task Planning**: Automated task decomposition and execution

### 🎨 Product Development Workflow
- **Ideation Canvas**: Visual board for organizing ideas, goals, features, and tasks
- **Project Management**: Complete project lifecycle from brainstorming to execution
- **Context-Aware AI**: AI that understands and references your project history
- **Real-time Collaboration**: Live updates and shared workspace

### 🛠️ Technical Excellence
- **Modern Stack**: React 18 + TypeScript frontend, Python FastAPI backend
- **Fast Development**: Bun for lightning-fast package management and builds
- **Production Ready**: Docker containers with Kubernetes deployment
- **Scalable Architecture**: Microservices design with async processing

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**: For the backend API
- **Bun**: For frontend development and package management
- **Docker**: For containerization (optional for local development)
- **NVIDIA API Key**: For AI functionality (get from [NVIDIA NIM](https://build.nvidia.com))

### 🏃‍♂️ Get Started in 3 Steps

1. **Quick Setup**:
   ```bash
   make quick-start
   ```

2. **Set Your API Key**:
   ```bash
   # Edit backend/.env and add your NVIDIA API key
   NIM_API_KEY=your_actual_nvidia_api_key_here
   ```

3. **Start the Application**:
   ```bash
   # Terminal 1: Start backend
   make backend-dev
   
   # Terminal 2: Start frontend
   make dev
   ```

4. **Visit the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

### 🔧 Manual Setup

If you prefer manual setup:

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install uv
uv pip install fastapi uvicorn sqlalchemy asyncpg httpx pydantic pydantic-settings numpy
python test_server.py
```

#### Frontend Setup
```bash
bun install
bun run dev
```

## 📚 API Documentation

The backend provides a comprehensive API for the agentic application:

- **Health Check**: `GET /health`
- **NVIDIA NIM Health**: `GET /api/v1/nim/health`
- **Chat with AI**: `POST /api/v1/nim/chat`
- **RAG Chat**: `POST /api/v1/rag/chat`
- **Agent Management**: `GET /api/v1/agents`
- **Task Management**: `GET /api/v1/tasks`

Visit http://localhost:8000/docs for interactive API documentation.

## 🔐 Security Setup

### Secure Environment Setup

For production-ready security, use the secure setup:

```bash
# Complete secure setup with security scanning
make secure-start
```

This will:
- ✅ Create secure environment variables with generated keys
- ✅ Run comprehensive security vulnerability scan
- ✅ Generate security report and fixes guide
- ✅ Set up both frontend and backend environments

### Security Commands

```bash
# Set up secure environment variables
make backend-env

# Run security vulnerability scan
make security-scan

# Generate security reports
make security-report

# Complete secure setup
make security-setup
```

### 🔒 Environment Variables

The application now uses secure environment variables instead of hardcoded secrets:

- **SECRET_KEY**: JWT signing key (auto-generated)
- **API_KEY**: API authentication key (auto-generated)
- **NIM_API_KEY**: Your NVIDIA API key (set manually)
- **POSTGRES_PASSWORD**: Database password (set manually)

**Important**: Always edit `backend/.env` to set your actual API keys before running the application.

### Kubernetes Deployment

To deploy the application to a Kubernetes cluster, you will need access to a container registry (like Docker Hub, GHCR, etc.) that your cluster can pull images from.

1.  **Configure the Registry in `values.yaml`:**
    Open `charts/frontend/values.yaml` and update the `image.repository` to point to your container registry and repository.

2.  **Build and Push the Image:**
    Use the `make` commands to build and push your image. You will need to be logged into your container registry (`podman login your-registry.io`).

    ```bash
    # Build the container image
    make podman-build

    # Tag the image with your repository and a version
    podman tag localhost/react-bun-k8s:latest your-registry.io/your-repo:latest

    # Push the image
    podman push your-registry.io/your-repo:latest
    ```

3.  **Deploy with Helm:**
    Use the `helm-upgrade` command from the `Makefile`. This will install or upgrade the release in the `web` namespace, creating it if it doesn't exist.

    ```bash
    make helm-upgrade
    ```

    If your repository is private, make sure you have created an `imagePullSecrets` in the `web` namespace and configured it in the `values.yaml` file.

4.  **Prerequisite: cert-manager for HTTPS**
    This chart is configured to use `cert-manager` to automatically provision and renew TLS certificates for HTTPS. If you don't have `cert-manager` installed in your cluster, you can install it with Helm:

    ```bash
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    helm install cert-manager jetstack/cert-manager \
      --namespace cert-manager \
      --create-namespace \
      --version v1.14.5 \
      --set installCRDs=true
    ```

## 🛠️ Makefile Commands

This project includes a comprehensive `Makefile` with convenient shortcuts for all tasks.

### 🚀 Quick Start Commands
- `make quick-start`: Set up backend environment for testing
- `make full-start`: Set up both frontend and backend for development
- `make secure-start`: Complete secure setup with security scanning
- `make help`: Show all available commands

### 🖥️ Development Commands
- `make dev`: Start frontend development server
- `make backend-dev`: Start backend development server
- `make backend-setup`: Set up backend Python environment
- `make backend-env`: Create secure environment variables file
- `make backend-test`: Test backend endpoints

### 🔐 Security Commands
- `make security-scan`: Run security vulnerability scan
- `make security-report`: Generate security report
- `make security-setup`: Set up secure environment and run security scan

### 🐳 Container Commands
- `make container-build`: Build both frontend and backend containers
- `make container-build-registry REGISTRY=your-registry`: Build and tag for registry
- `make container-run`: Run both containers locally
- `make container-stop`: Stop running containers
- `make container-push REGISTRY=your-registry`: Push containers to registry

### ☸️ Kubernetes Commands
- `make helm-install`: Install Helm chart
- `make helm-upgrade`: Upgrade Helm release
- `make deploy`: Deploy to Kubernetes

## 📁 Project Structure

```
hack-a-product/
├── 📁 backend/                 # Python FastAPI backend
│   ├── 📁 src/agentic_app/     # Main application code
│   │   ├── 📁 api/v1/          # API endpoints
│   │   ├── 📁 models/          # Database models
│   │   ├── 📁 services/        # Business logic
│   │   └── 📁 core/            # Configuration and database
│   ├── 📄 Dockerfile           # Backend container
│   ├── 📄 pyproject.toml       # Python dependencies
│   ├── 📄 env.example          # Environment variables template
│   └── 📄 .env                 # Environment variables (git-ignored)
├── 📁 src/                     # React frontend
│   ├── 📁 components/          # UI components
│   └── 📄 App.tsx              # Main application
├── 📁 charts/                  # Helm charts
│   ├── 📁 frontend/            # Frontend deployment
│   └── 📁 backend/             # Backend deployment
├── 📄 Makefile                 # Development commands
├── 📄 setup_env.sh             # Environment setup script
├── 📄 security_scan.sh         # Security vulnerability scanner
├── 📄 SECURITY_REPORT.md       # Security analysis report
├── 📄 SECURITY_FIXES.md        # Security fixes guide
└── 📄 README.md                # This file
```

## 🧪 Testing the Application

### Backend Testing
```bash
# Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/nim/health

# Test AI chat (requires NVIDIA API key)
curl -X POST http://localhost:8000/api/v1/nim/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "max_tokens": 100}'

# Test RAG functionality
curl -X POST http://localhost:8000/api/v1/rag/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the main features?"}'
```

### Frontend Testing
1. Visit http://localhost:3000
2. Check that the UI loads with "The Product Mindset" branding
3. Verify agent and task displays are working
4. Test the chat interface

## 🔮 Future Enhancements

- **Ideation Canvas**: Visual drag-and-drop interface for project management
- **Real-time Collaboration**: WebSocket-based live updates
- **Advanced RAG**: Vector database integration (ChromaDB/Pinecone)
- **Multi-modal AI**: Image and document processing capabilities
- **Agent Workflows**: Multi-step autonomous task execution
- **GitOps Integration**: ArgoCD/FluxCD for automated deployments

## 📄 Documentation

- **[Hackathon Requirements](HACKATHON.md)**: Detailed compliance documentation
- **[NVIDIA NIM Integration](NIM_INTEGRATION_GUIDE.md)**: AI service setup guide
- **[Testing Guide](TESTING_GUIDE.md)**: Comprehensive testing instructions
- **[Security Report](SECURITY_REPORT.md)**: Security vulnerability analysis
- **[Security Fixes](SECURITY_FIXES.md)**: Step-by-step security implementation guide
- **[Container Registry Guide](CONTAINER_REGISTRY_GUIDE.md)**: Container registry setup and deployment
- **[Submission Summary](SUBMISSION_SUMMARY.md)**: Hackathon submission details