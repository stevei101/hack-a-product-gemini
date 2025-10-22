# Makefile for The Product Mindset - Agentic Application
# Provides convenient commands for development, building, and deployment

.PHONY: help dev build test clean container-build container-run container-push deploy check-prerequisites

# Default target
help: ## Show this help message
	@echo "The Product Mindset - Agentic Application"
	@echo "=========================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Frontend Development commands
install: ## Install frontend dependencies
	bun install

dev: ## Start frontend development server
	bun run dev

build: ## Build the React application
	bun run build

preview: ## Preview the built application
	bun run preview

test: ## Run tests (placeholder - add your test command here)
	@echo "No tests configured yet. Add your test command to package.json"

# Backend Development commands
backend-dev: ## Start backend development server
	cd backend && source .venv/bin/activate && PYTHONPATH="${CURDIR}/backend/src:${PYTHONPATH}" python3 test_server.py

backend-setup: ## Set up backend environment
	@echo "🔧 Setting up backend with uv..."
	@if ! command -v uv &> /dev/null; then \
		echo "📦 Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@if [ ! -d "backend/.venv" ]; then \
		echo "🐍 Creating virtual environment with uv..."; \
		cd backend && uv venv; \
	fi
	@echo "📦 Installing dependencies with uv..."
	cd backend && uv pip install fastapi uvicorn sqlalchemy asyncpg httpx pydantic pydantic-settings python-dotenv redis numpy openai pytest pytest-asyncio pytest-cov fakeredis

backend-env: ## Copy environment variables template
	@if [ ! -f "backend/.env" ]; then \
		cp backend/env.example backend/.env; \
		echo "✅ Created backend/.env from template"; \
		echo "⚠️  Please edit backend/.env and set your NVIDIA API key"; \
	else \
		echo "✅ backend/.env already exists"; \
	fi

backend-install: ## Install backend dependencies from requirements.txt
	@echo "📦 Installing backend dependencies from requirements.txt..."
	@if ! command -v uv &> /dev/null; then \
		echo "❌ uv not found. Run 'make backend-setup' first"; \
		exit 1; \
	fi
	cd backend && uv pip install -r requirements.txt

backend-install-dev: ## Install backend dev dependencies
	@echo "📦 Installing backend dev dependencies..."
	@if ! command -v uv &> /dev/null; then \
		echo "❌ uv not found. Run 'make backend-setup' first"; \
		exit 1; \
	fi
	cd backend && uv pip install -r requirements.txt -r requirements-dev.txt

backend-test: ## Run backend tests
	@echo "🧪 Running backend tests..."
	cd backend && source .venv/bin/activate && PYTHONPATH="${CURDIR}/backend/src:${PYTHONPATH}" pytest tests/ -v

backend-test-quick: ## Run backend tests (quick)
	@echo "🧪 Running quick backend tests..."
	cd backend && source .venv/bin/activate && PYTHONPATH="${CURDIR}/backend/src:${PYTHONPATH}" ./scripts/test_quick.sh

backend-test-coverage: ## Run backend tests with coverage
	@echo "📊 Running tests with coverage..."
	cd backend && source .venv/bin/activate && PYTHONPATH="${CURDIR}/backend/src:${PYTHONPATH}" ./scripts/run_tests.sh coverage

backend-api-test: ## Test backend API endpoints
	@echo "Testing backend endpoints..."
	@curl -s http://localhost:8000/health | head -5
	@curl -s http://localhost:8000/api/v1/nim/health | head -5

backend-logs: ## View backend logs
	@echo "Backend logs (if running):"
	@ps aux | grep test_server | grep -v grep

backend-clean: ## Clean backend virtual environment and cache
	@echo "🧹 Cleaning backend environment..."
	rm -rf backend/.venv
	rm -rf backend/__pycache__
	rm -rf backend/src/agentic_app/__pycache__
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Backend cleaned"

backend-reset: backend-clean backend-setup ## Reset backend environment completely
	@echo "🔄 Backend environment reset complete!"

# Service commands
services-start: ## Start PostgreSQL and Redis services using Podman
	./start_services.sh

services-stop: ## Stop PostgreSQL and Redis services
	@echo "🛑 Stopping development services..."
	podman stop postgres-dev redis-dev 2>/dev/null || true
	@echo "✅ Services stopped"

services-status: ## Check status of development services
	@echo "📊 Service Status:"
	@podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "postgres-dev|redis-dev|NAMES" || echo "No services running"

services-clean: ## Remove PostgreSQL and Redis containers
	@echo "🗑️  Removing development service containers..."
	podman stop postgres-dev redis-dev 2>/dev/null || true
	podman rm postgres-dev redis-dev 2>/dev/null || true
	@echo "✅ Service containers removed"

# Security commands
security-scan: ## Run security vulnerability scan
	./security_scan.sh

security-report: ## Generate security report
	@echo "🔍 Security Report Generated"
	@echo "📄 Check SECURITY_REPORT.md for detailed findings"
	@echo "🔧 Check SECURITY_FIXES.md for implementation guide"

security-setup: ## Set up secure environment and run security scan
	@echo "🔐 Setting up secure environment..."
	@make backend-env
	@echo "🔍 Running security scan..."
	./security_scan.sh

clean: ## Clean build artifacts (frontend only)
	rm -rf dist/
	rm -rf node_modules/

clean-all: clean backend-clean ## Clean all build artifacts and environments
	@echo "✅ All cleaned!"

# Container commands (uses Podman)
container-build: ## Build container images for both frontend and backend
	@echo "Building frontend container..."
	podman build -t smithveunsa/react-bun-k8s:frontend .
	@echo "Building backend container..."
	podman build -t smithveunsa/react-bun-k8s:backend ./backend

container-build-registry: ## Build and tag for registry (usage: make container-build-registry REGISTRY=ghcr.io/username)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "❌ Please specify REGISTRY (e.g., make container-build-registry REGISTRY=ghcr.io/username)"; \
		exit 1; \
	fi
	@echo "Building and tagging for registry: $(REGISTRY)"
	podman build -t $(REGISTRY):frontend .
	podman build -t $(REGISTRY):backend ./backend

container-run: ## Run containers locally
	@echo "Starting backend container..."
	podman run -d --name backend -p 8000:8000 smithveunsa/react-bun-k8s:backend
	@echo "Starting frontend container..."
	podman run -d --name frontend -p 3000:80 smithveunsa/react-bun-k8s:frontend
	@echo "✅ Containers started! Backend: http://localhost:8000, Frontend: http://localhost:3000"

container-stop: ## Stop running containers
	podman stop backend frontend || true
	podman rm backend frontend || true

container-push: ## Push containers to registry (usage: make container-push REGISTRY=ghcr.io/username)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "❌ Please specify REGISTRY (e.g., make container-push REGISTRY=ghcr.io/username)"; \
		exit 1; \
	fi
	@echo "Pushing to registry: $(REGISTRY)"
	podman push $(REGISTRY):frontend
	podman push $(REGISTRY):backend

# GitHub Actions Deployment commands
github-secrets: ## Show required GitHub repository secrets
	@echo "🔐 Required GitHub Repository Secrets:"
	@echo "  AWS_ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT:role/product-mindset-github-actions-dev"
	@echo "  AWS_REGION=us-east-1"
	@echo "  NIM_API_KEY=your_nvidia_api_key"
	@echo "  POSTGRES_PASSWORD=your_secure_password"
	@echo ""
	@echo "📝 Add these secrets in GitHub: Settings → Secrets and variables → Actions"

github-deploy: ## Trigger GitHub Actions deployment
	@echo "🚀 Triggering GitHub Actions deployment..."
	@echo "📝 Push to 'main' or 'develop' branch to trigger deployment"
	@echo "🔗 Check Actions tab in your GitHub repository"

github-troubleshoot: ## Troubleshoot GitHub Actions AWS OIDC issues
	@echo "🔍 Running AWS OIDC troubleshooting..."
	./scripts/troubleshoot-aws-oidc.sh

github-test-auth: ## Test GitHub Actions AWS authentication
	@echo "🧪 Testing GitHub Actions AWS authentication..."
	@echo "📝 Push to 'develop' branch to trigger AWS auth test"
	@echo "🔗 Check Actions tab for 'Test AWS Authentication' workflow"

github-verify: ## Verify GitHub repository configuration
	@echo "🔍 Verifying GitHub repository setup..."
	./scripts/verify-github-setup.sh

github-config: ## Check GitHub configuration checklist
	@echo "📋 GitHub configuration checklist..."
	./scripts/check-github-config.sh

# Terraform Cloud commands (for infrastructure management)
terraform-validate: ## Validate Terraform configuration locally
	cd terraform && terraform validate

terraform-format: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Helm commands
helm-install: ## Install Helm chart
	helm install frontend ./charts/frontend --namespace web --create-namespace

helm-upgrade: ## Upgrade Helm chart
	helm upgrade --install frontend ./charts/frontend --namespace web

helm-uninstall: ## Uninstall Helm chart
	helm uninstall frontend --namespace web

# Kubernetes management
k8s: ## Manage local Kubernetes cluster (usage: make k8s command)
	./scripts/k8s-manage.sh $(filter-out $@,$(MAKECMDGOALS))

# Full workflow commands
deploy-local: ## Deploy to local Kubernetes (minikube/kind)
	./scripts/deploy.sh local latest

deploy-staging: ## Deploy to staging environment
	./scripts/deploy.sh staging staging

deploy-production: ## Deploy to production environment
	./scripts/deploy.sh production latest

# Quick start commands
quick-start: backend-env backend-setup ## Quick start for testing
	@echo "🚀 Setting up The Product Mindset for testing..."
	@echo "✅ Backend environment ready!"
	@echo "📝 Next steps:"
	@echo "  1. Edit backend/.env and set your NVIDIA API key"
	@echo "  2. Run 'make services-start' to start PostgreSQL and Redis"
	@echo "  3. Run 'make backend-dev' to start the backend"
	@echo "  4. Run 'make dev' to start the frontend"
	@echo "  5. Visit http://localhost:5173 for the UI"
	@echo "  6. Visit http://localhost:8000/docs for API docs"

full-start: backend-env backend-setup ## Complete setup for development
	@echo "🚀 Setting up The Product Mindset for full development..."
	@echo "✅ Frontend and backend environments ready!"
	@echo "📝 Next steps:"
	@echo "  1. Edit backend/.env and set your NVIDIA API key"
	@echo "  2. Run 'make services-start' to start PostgreSQL and Redis"
	@echo "  3. Run 'make backend-dev' to start the backend"
	@echo "  4. Run 'make dev' to start the frontend"
	@echo "  5. Visit http://localhost:5173 for the UI"
	@echo "  6. Visit http://localhost:8000/docs for API docs"

secure-start: security-setup backend-setup ## Complete secure setup with security scan
	@echo "🔐 Setting up The Product Mindset with security best practices..."
	@echo "✅ Secure environment ready!"
	@echo "📝 Next steps:"
	@echo "  1. Edit backend/.env and set your NVIDIA API key"
	@echo "  2. Run 'make services-start' to start PostgreSQL and Redis"
	@echo "  3. Run 'make backend-dev' to start the backend"
	@echo "  4. Run 'make dev' to start the frontend"
	@echo "  5. Review security report in SECURITY_REPORT.md"

# Complete setup commands
full-setup: check-prerequisites install k8s-setup ## Complete setup including Kubernetes
	@echo "🎉 Complete environment ready!"
	@echo "Run 'make deploy' to deploy your app"
