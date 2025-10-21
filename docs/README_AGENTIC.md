# Agentic Application

An intelligent agentic application built with React, FastAPI, and NVIDIA NIM, featuring the llama-3 1-nemotron-nano-8B-v1 large language model with advanced reasoning capabilities.

## 🎯 Overview

This application demonstrates a complete agentic system that can:
- **Reason** about complex tasks using AI
- **Plan** and execute multi-step workflows
- **Learn** from interactions and improve over time
- **Scale** on AWS EKS with NVIDIA GPU support

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend│    │  NVIDIA NIM     │
│   (Agent UI)    │◄──►│   (Agent Logic) │◄──►│  Services       │
│                 │    │                 │    │                 │
│ • Chat Interface│    │ • Agent Manager │    │ • LLM Inference │
│ • Task Display  │    │ • Task Planner  │    │ • Embeddings    │
│ • Status Monitor│    │ • Memory Store  │    │ • Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   AWS EKS/      │
                    │   SageMaker     │
                    │   Infrastructure│
                    └─────────────────┘
```

## 🚀 Features

### AI Agent Capabilities
- **Intelligent Reasoning**: Powered by llama-3 1-nemotron-nano-8B-v1
- **Task Planning**: Autonomous task decomposition and execution
- **Memory Management**: Persistent agent memory and context
- **Multi-Agent Coordination**: Multiple agents working together
- **Real-time Communication**: WebSocket-based agent updates

### Technical Features
- **Modern Stack**: React + TypeScript frontend, Python FastAPI backend
- **NVIDIA NIM Integration**: High-performance inference microservices
- **Vector Database**: ChromaDB for embeddings and semantic search
- **Containerized**: Docker containers for consistent deployment
- **Kubernetes Ready**: Helm charts for AWS EKS deployment
- **Scalable**: Auto-scaling based on demand

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Bun** for fast development

### Backend
- **FastAPI** with Python 3.11
- **SQLAlchemy** with async support
- **PostgreSQL** with asyncpg
- **Redis** for caching and task queues
- **uv** for Python package management

### AI/ML Services
- **NVIDIA NIM** inference microservice
- **llama-3 1-nemotron-nano-8B-v1** for reasoning
- **NVIDIA Nemotron-3-Embedding** for embeddings
- **ChromaDB** for vector storage

### Infrastructure
- **AWS EKS** for orchestration
- **Docker** for containerization
- **Helm** for deployment management
- **NGINX Ingress** for load balancing

## 📋 Prerequisites

- **Docker** and **Docker Compose**
- **Kubernetes** cluster (AWS EKS recommended)
- **NVIDIA GPU** support for NIM services
- **Python 3.11+** for backend development
- **Node.js 18+** or **Bun** for frontend development

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd hack-a-product

# Copy environment files
cp backend/env.example backend/.env
```

### 2. Configure Environment

Edit `backend/.env` with your configuration:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=agentic_app

# NVIDIA NIM
NIM_BASE_URL=http://localhost:8000/v1
NIM_API_KEY=your-nim-api-key
NIM_MODEL_NAME=meta/llama-3.1-8b-instruct
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Development

### Backend Development

```bash
cd backend

# Install dependencies with uv
uv pip install -e .

# Run development server
uvicorn agentic_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Install dependencies
bun install

# Start development server
bun run dev
```

## 🚀 Deployment

### AWS EKS Deployment

1. **Create EKS Cluster**

```bash
eksctl create cluster \
  --name agentic-cluster \
  --region us-west-2 \
  --nodegroup-name worker-nodes \
  --node-type g4dn.xlarge \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --with-oidc \
  --ssh-access \
  --ssh-public-key your-key
```

2. **Deploy with Helm**

```bash
# Add NVIDIA Helm repository
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Deploy NVIDIA NIM
helm install nim nvidia/nim \
  --set image.repository=nvcr.io/nim/meta/llama-3.1-8b-instruct \
  --set resources.requests.nvidia.com/gpu=1

# Deploy backend
helm install backend ./charts/backend

# Deploy frontend
helm install frontend ./charts/frontend
```

### Environment Variables

Configure the following environment variables for production:

```bash
# Database
POSTGRES_SERVER=your-postgres-host
POSTGRES_PASSWORD=your-secure-password

# NVIDIA NIM
NIM_BASE_URL=https://your-nim-endpoint/v1
NIM_API_KEY=your-production-api-key

# Security
SECRET_KEY=your-secure-secret-key
```

## 📊 API Usage

### Create an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "description": "An agent specialized in research tasks",
    "capabilities": ["research", "analysis", "summarization"]
  }'
```

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Market Research",
    "description": "Research the latest trends in AI technology",
    "priority": "high",
    "agent_id": 1
  }'
```

### Chat with AI

```bash
curl -X POST "http://localhost:8000/api/v1/nim/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

## 🔍 Monitoring

### Health Checks

- **Backend Health**: `GET /health`
- **NIM Health**: `GET /api/v1/nim/health`
- **Database Status**: Check PostgreSQL connectivity

### Metrics

The application exposes Prometheus metrics at `/metrics`:

- Request rates and latencies
- Agent task completion rates
- GPU utilization (for NIM services)
- Database connection pools

## 🛡️ Security

### Authentication
- JWT-based authentication (to be implemented)
- API key authentication for NIM services
- RBAC for Kubernetes resources

### Network Security
- TLS encryption for all communications
- Network policies for pod-to-pod communication
- Ingress with SSL termination

## 📈 Scaling

### Horizontal Scaling
- Auto-scaling based on CPU/memory usage
- Multiple agent instances for high availability
- Load balancing across multiple NIM instances

### Vertical Scaling
- GPU resource allocation for NIM services
- Memory optimization for large models
- Database connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the `/docs` folder
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] Basic agent creation and management
- [x] Task planning and execution
- [x] NVIDIA NIM integration
- [x] Web interface

### Phase 2: Advanced Features 🚧
- [ ] Multi-agent coordination
- [ ] Advanced memory systems
- [ ] Tool integration
- [ ] Performance optimization

### Phase 3: Production Features 📋
- [ ] Authentication and authorization
- [ ] Advanced monitoring
- [ ] Cost optimization
- [ ] Multi-cloud deployment

---

**Built with ❤️ using React, FastAPI, NVIDIA NIM, and AWS EKS**
