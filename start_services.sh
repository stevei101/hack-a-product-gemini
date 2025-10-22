#!/bin/bash
# Start development services using Podman
# This script starts PostgreSQL and Redis containers for local development

set -e

echo "🚀 Starting development services with Podman..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# PostgreSQL configuration
POSTGRES_CONTAINER="postgres-dev"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-your_secure_postgres_password_here}"
POSTGRES_DB="agentic_app"
POSTGRES_PORT="5432"

# Redis configuration
REDIS_CONTAINER="redis-dev"
REDIS_PORT="6379"

# Function to check if container exists
container_exists() {
    podman ps -a --format "{{.Names}}" | grep -q "^$1$"
}

# Function to check if container is running
container_running() {
    podman ps --format "{{.Names}}" | grep -q "^$1$"
}

# Start PostgreSQL
echo -e "${YELLOW}📦 Setting up PostgreSQL...${NC}"
if container_running "$POSTGRES_CONTAINER"; then
    echo -e "${GREEN}✅ PostgreSQL is already running${NC}"
elif container_exists "$POSTGRES_CONTAINER"; then
    echo -e "${YELLOW}⚡ Starting existing PostgreSQL container...${NC}"
    podman start "$POSTGRES_CONTAINER"
    echo -e "${GREEN}✅ PostgreSQL started${NC}"
else
    echo -e "${YELLOW}🆕 Creating new PostgreSQL container...${NC}"
    podman run --name "$POSTGRES_CONTAINER" \
        -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
        -e POSTGRES_DB="$POSTGRES_DB" \
        -p "$POSTGRES_PORT:5432" \
        -d postgres:16
    echo -e "${GREEN}✅ PostgreSQL created and started${NC}"
fi

# Start Redis
echo -e "${YELLOW}📦 Setting up Redis...${NC}"
if container_running "$REDIS_CONTAINER"; then
    echo -e "${GREEN}✅ Redis is already running${NC}"
elif container_exists "$REDIS_CONTAINER"; then
    echo -e "${YELLOW}⚡ Starting existing Redis container...${NC}"
    podman start "$REDIS_CONTAINER"
    echo -e "${GREEN}✅ Redis started${NC}"
else
    echo -e "${YELLOW}🆕 Creating new Redis container...${NC}"
    podman run --name "$REDIS_CONTAINER" \
        -p "$REDIS_PORT:6379" \
        -d redis:7-alpine
    echo -e "${GREEN}✅ Redis created and started${NC}"
fi

# Wait a moment for services to be ready
echo ""
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 3

# Verify services are running
echo ""
echo -e "${YELLOW}🔍 Verifying services...${NC}"
if container_running "$POSTGRES_CONTAINER" && container_running "$REDIS_CONTAINER"; then
    echo -e "${GREEN}✅ All services are running!${NC}"
    echo ""
    echo "📊 Service Status:"
    podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "postgres-dev|redis-dev|NAMES"
    echo ""
    echo -e "${GREEN}🎉 Development environment is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Ensure backend/.env has your NVIDIA API key"
    echo "  2. Run 'make backend-dev' in one terminal"
    echo "  3. Run 'make dev' in another terminal"
    echo ""
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    exit 1
fi

