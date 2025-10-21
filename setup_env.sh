#!/bin/bash

# Environment Setup Script for The Product Mindset
# This script helps you set up secure environment variables

set -e

echo "🔐 Setting up secure environment variables for The Product Mindset"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local status=$1
    local message=$2
    case $status in
        "INFO")
            echo -e "${BLUE}ℹ️  INFO:${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  WARNING:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}❌ ERROR:${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✅ SUCCESS:${NC} $message"
            ;;
    esac
}

# Check if .env file already exists
if [ -f "backend/.env" ]; then
    print_status "WARNING" "backend/.env already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "INFO" "Setup cancelled"
        exit 0
    fi
fi

# Create backend directory if it doesn't exist
mkdir -p backend

print_status "INFO" "Creating secure environment configuration..."

# Generate secure random keys
SECRET_KEY=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 32)

# Create .env file
cat > backend/.env << EOF
# Development Environment Variables
# DO NOT COMMIT THIS FILE TO VERSION CONTROL
# Generated on $(date)

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password_123
POSTGRES_DB=agentic_app
POSTGRES_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379

# NVIDIA NIM Configuration
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_API_KEY=your_nvidia_api_key_here
NIM_MODEL_NAME=nvidia/llama-3_1-nemotron-nano-8b-v1
NIM_EMBEDDING_MODEL=nvidia/nv-embedqa-e5-v5

# Agent Configuration
MAX_CONCURRENT_AGENTS=10
AGENT_TIMEOUT_SECONDS=300
MAX_TASK_RETRIES=3

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_DIMENSION=1024

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security (Generated secure keys)
SECRET_KEY=$SECRET_KEY
API_KEY=$API_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
EOF

print_status "SUCCESS" "Environment file created at backend/.env"

echo ""
print_status "INFO" "🔑 IMPORTANT: You need to set your NVIDIA API key:"
echo "   1. Get your NVIDIA API key from: https://build.nvidia.com"
echo "   2. Edit backend/.env and replace 'your_nvidia_api_key_here' with your actual API key"
echo "   3. For production, use strong passwords for POSTGRES_PASSWORD"

echo ""
print_status "INFO" "📝 Next steps:"
echo "   1. Edit backend/.env and set your NVIDIA API key"
echo "   2. Run: make backend-setup"
echo "   3. Run: make backend-dev"

echo ""
print_status "WARNING" "🔒 Security reminders:"
echo "   • Never commit .env files to version control"
echo "   • Use strong, unique passwords in production"
echo "   • Rotate API keys regularly"
echo "   • Use environment-specific .env files"

print_status "SUCCESS" "Environment setup complete!"