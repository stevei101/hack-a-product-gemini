# Local Development Environment Setup

This guide will help you set up the local development environment for The Product Mindset agentic application.

## ✅ Prerequisites Installed

- ✅ **Python 3.10+** - Backend runtime
- ✅ **Bun** - Frontend package manager and runtime
- ✅ **uv** - Fast Python package installer
- ✅ **Podman** - Container runtime (Docker alternative)
- ✅ **Minikube** - Local Kubernetes cluster (with k3s)
- ✅ **Helm** - Kubernetes package manager
- ✅ **kubectl** - Kubernetes CLI
- **Git** - Version control

## 📦 What's Already Set Up

1. ✅ Frontend dependencies installed via Bun
2. ✅ Backend Python virtual environment created with uv
3. ✅ All Python dependencies installed (FastAPI, SQLAlchemy, ChromaDB, etc.)
4. ✅ Environment configuration file created (`backend/.env`)
5. ✅ Minikube cluster running with k3s
6. ✅ Helm charts available for deployment

## 🔧 Development Modes

You can run the application in two modes:

### Mode 1: Direct Local Development (Simple)

Run services directly on your machine using Podman containers for databases.

**Start Services:**
```bash
# Start PostgreSQL and Redis using Podman
make services-start

# Check service status
make services-status
```

This will start:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

### Mode 2: Kubernetes Development (Advanced)

Deploy to local Minikube cluster using Helm charts.

**Prerequisites:**
```bash
# Ensure Minikube is running
minikube status

# If not running, start it
minikube start --driver=podman --container-runtime=cri-o

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

**Deploy with Helm:**
```bash
# Deploy backend to Minikube
make helm-install-backend

# Deploy frontend to Minikube
make helm-install-frontend

# Check deployment status
kubectl get pods -n web
```

## 🔑 Environment Configuration

Edit `backend/.env` and set these required values:

```bash
# NVIDIA API Key (REQUIRED)
NIM_API_KEY=your_nvidia_nim_api_key_here

# Database Password (if using different password)
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Security Keys (generate secure random strings)
SECRET_KEY=your_jwt_secret_key_here
API_KEY=your_api_authentication_key_here
```

### Get Your NVIDIA API Key

1. Visit [NVIDIA NIM](https://build.nvidia.com)
2. Sign in or create an account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your `.env` file

### Generate Secure Keys

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate API_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🚀 Starting the Development Servers

### Terminal 1: Start Backend

```bash
# Activate virtual environment and start backend
cd backend
source .venv/bin/activate
python3 test_server.py

# OR use the Makefile command
make backend-dev
```

The backend will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Terminal 2: Start Frontend

```bash
# Start frontend development server
bun run dev

# OR use the Makefile command
make dev
```

The frontend will be available at:
- UI: http://localhost:5173 (Vite default port)

## 📝 Quick Commands Reference

### Frontend Commands
```bash
make install          # Install frontend dependencies
make dev              # Start frontend dev server
make build            # Build for production
make preview          # Preview production build
```

### Backend Commands
```bash
make backend-setup    # Set up backend virtual environment
make backend-env      # Create .env file from template
make backend-dev      # Start backend dev server
make backend-test     # Test backend endpoints
make backend-logs     # View backend logs
```

### Service Management (Podman)
```bash
make services-start   # Start PostgreSQL and Redis
make services-stop    # Stop all services
make services-status  # Check service status
make services-clean   # Remove service containers
```

### Container Commands (Podman)
```bash
make container-build  # Build container images
make container-run    # Run containers locally
make container-stop   # Stop containers
```

### Kubernetes Commands (Minikube + Helm)
```bash
make k8s-start        # Start Minikube cluster
make k8s-stop         # Stop Minikube cluster
make k8s-status       # Check cluster status
make helm-install     # Install all Helm charts
make helm-upgrade     # Upgrade Helm releases
make helm-uninstall   # Uninstall Helm charts
```

### Quick Setup Commands
```bash
make quick-start      # Quick setup for testing
make full-start       # Complete development setup
make secure-start     # Secure setup with security scan
```

## 🧪 Verify Your Setup

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/nim/health
```

### 2. Check Frontend

Open http://localhost:5173 in your browser - you should see the Product Mindset UI.

### 3. Test API Documentation

Visit http://localhost:8000/docs - you should see the interactive API documentation.

## 🗂️ Project Structure

```
hack-a-product-gemini/
├── backend/                 # FastAPI backend
│   ├── src/agentic_app/    # Application code
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── .env                # Environment variables
│   ├── .venv/              # Python virtual environment
│   └── pyproject.toml      # Python dependencies
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── App.tsx            # Main app component
│   └── index.tsx          # Entry point
├── package.json           # Frontend dependencies
└── vite.config.ts         # Vite configuration
```

## 🐛 Troubleshooting

### Backend won't start

1. **Check PostgreSQL is running:**
   ```bash
   make services-status
   # OR
   podman ps | grep postgres
   ```

2. **Check Redis is running:**
   ```bash
   podman ps | grep redis
   ```

3. **Verify .env file:**
   ```bash
   cat backend/.env | grep NIM_API_KEY
   ```

4. **Check virtual environment:**
   ```bash
   cd backend && source .venv/bin/activate && python --version
   ```

### Frontend won't start

1. **Clear node_modules and reinstall:**
   ```bash
   rm -rf node_modules bun.lock
   bun install
   ```

2. **Check for port conflicts:**
   ```bash
   lsof -i :5173
   ```

### Database connection errors

1. **Test PostgreSQL connection:**
   ```bash
   podman exec -it postgres-dev psql -U postgres -d agentic_app
   ```

2. **Check credentials in .env match your PostgreSQL setup**

3. **Restart PostgreSQL container:**
   ```bash
   make services-stop
   make services-start
   ```

### Minikube issues

1. **Check Minikube status:**
   ```bash
   minikube status
   ```

2. **Restart Minikube:**
   ```bash
   minikube stop
   minikube start --driver=podman
   ```

3. **Check cluster resources:**
   ```bash
   kubectl get nodes
   kubectl get pods -A
   ```

4. **View Minikube logs:**
   ```bash
   minikube logs
   ```

### Helm deployment issues

1. **List Helm releases:**
   ```bash
   helm list -A
   ```

2. **Check pod logs:**
   ```bash
   kubectl logs -n web <pod-name>
   ```

3. **Describe failing pod:**
   ```bash
   kubectl describe pod -n web <pod-name>
   ```

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use strong, unique passwords for all services
- Rotate API keys regularly
- Keep dependencies up to date: `uv pip list --outdated`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [Bun Documentation](https://bun.sh/docs)
- [uv Documentation](https://github.com/astral-sh/uv)

## 🎯 Next Steps

1. ✅ Set up your NVIDIA API key in `backend/.env`
2. ✅ Start PostgreSQL and Redis services
3. ✅ Start the backend server (`make backend-dev`)
4. ✅ Start the frontend server (`make dev`)
5. 🚀 Start building!

For deployment to production, see the deployment documentation in `/docs`.

