# Testing Guide - The Product Mindset

## 🚀 Quick Start Testing

### Prerequisites
- Python 3.11+
- Bun (for frontend)
- PostgreSQL (or Docker for database)
- Redis (or Docker for cache)
- NVIDIA API Key (for testing NIM integration)

## 📋 Testing Steps

### Step 1: Backend Setup & Testing

#### 1.1 Install Python Dependencies
```bash
cd backend

# Install uv if you don't have it
pip install uv

# Install dependencies
uv pip install -e .

# Or install manually
pip install fastapi uvicorn sqlalchemy asyncpg httpx
```

#### 1.2 Set Up Environment Variables
```bash
# Copy environment file
cp env.example .env

# Edit .env with your settings
NIM_API_KEY=your_nvidia_api_key_here
POSTGRES_PASSWORD=your_password
```

#### 1.3 Start Backend Server
```bash
# Start the FastAPI server
uvicorn agentic_app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Python directly
python -m uvicorn agentic_app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 1.4 Test Backend Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Test NVIDIA NIM health
curl http://localhost:8000/api/v1/nim/health
```

### Step 2: Frontend Setup & Testing

#### 2.1 Install Frontend Dependencies
```bash
# From project root
bun install
```

#### 2.2 Start Frontend Development Server
```bash
bun run dev
```

#### 2.3 Test Frontend
```bash
# Open in browser
open http://localhost:3000
```

### Step 3: Database Setup (Optional for Testing)

#### 3.1 Using Docker (Recommended)
```bash
# Start PostgreSQL
docker run --name postgres-test -e POSTGRES_PASSWORD=password -e POSTGRES_DB=agentic_app -p 5432:5432 -d postgres:15

# Start Redis
docker run --name redis-test -p 6379:6379 -d redis:7-alpine
```

#### 3.2 Test Database Connection
```bash
# Test PostgreSQL
psql -h localhost -U postgres -d agentic_app

# Test Redis
redis-cli ping
```

## 🧪 Testing Scenarios

### Scenario 1: Basic Backend Health Check
```bash
# Test root endpoint
curl http://localhost:8000/

# Expected: {"message": "Agentic Application API", "version": "1.0.0"}

# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status": "healthy"}
```

### Scenario 2: NVIDIA NIM Integration Test
```bash
# Test NIM health (requires API key)
curl http://localhost:8000/api/v1/nim/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/nim/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Scenario 3: RAG Pipeline Test
```bash
# Test RAG chat endpoint
curl -X POST http://localhost:8000/api/v1/rag/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the main features of this project?",
    "project_id": 1
  }'

# Test embedding status
curl http://localhost:8000/api/v1/rag/embeddings/status
```

### Scenario 4: Agent Management Test
```bash
# Create an agent
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "description": "An agent specialized in research tasks",
    "capabilities": ["research", "analysis", "summarization"]
  }'

# List agents
curl http://localhost:8000/api/v1/agents
```

### Scenario 5: Task Management Test
```bash
# Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Market Research",
    "description": "Research the latest trends in AI technology",
    "priority": "high",
    "agent_id": 1
  }'

# List tasks
curl http://localhost:8000/api/v1/tasks
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Make sure you're in the right directory
cd backend/src

# Install in development mode
uv pip install -e .
```

#### 2. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U postgres -d agentic_app -c "SELECT 1;"
```

#### 3. NVIDIA API Issues
```bash
# Test API key
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "nvidia/llama-3_1-nemotron-nano-8b-v1",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'
```

#### 4. Frontend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check frontend build
bun run build
```

## 📊 Expected Results

### Backend API Endpoints
- ✅ `GET /` - Returns API info
- ✅ `GET /health` - Returns health status
- ✅ `GET /docs` - Swagger documentation
- ✅ `GET /api/v1/nim/health` - NVIDIA NIM status
- ✅ `POST /api/v1/nim/chat` - Chat with NVIDIA NIM
- ✅ `POST /api/v1/rag/chat` - RAG-powered chat
- ✅ `GET /api/v1/rag/embeddings/status` - Embedding status

### Frontend Features
- ✅ Loading screen with "The Product Mindset" branding
- ✅ Agent management interface
- ✅ Chat interface with AI
- ✅ Task queue visualization
- ✅ Responsive design

## 🎯 Success Criteria

1. **Backend starts without errors**
2. **Frontend loads and displays correctly**
3. **API endpoints respond correctly**
4. **NVIDIA NIM integration works** (with valid API key)
5. **RAG pipeline functions** (embeddings and retrieval)
6. **Database connections work** (if configured)

## 🔧 Development Tips

### Hot Reload
```bash
# Backend with auto-reload
uvicorn agentic_app.main:app --reload

# Frontend with auto-reload
bun run dev
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug
python -m uvicorn agentic_app.main:app --reload --log-level debug
```

### API Testing
```bash
# Use the built-in Swagger UI
open http://localhost:8000/docs

# Or use curl for command line testing
curl -X GET http://localhost:8000/api/v1/agents
```

## 📝 Testing Checklist

- [ ] Backend starts successfully
- [ ] Frontend loads without errors
- [ ] Health endpoints respond
- [ ] API documentation accessible
- [ ] NVIDIA NIM health check works
- [ ] Chat endpoint responds
- [ ] RAG endpoints function
- [ ] Agent CRUD operations work
- [ ] Task CRUD operations work
- [ ] Frontend-backend communication works

## 🚀 Next Steps After Testing

1. **Add real NVIDIA API key** for full functionality
2. **Set up database** for persistent storage
3. **Test RAG pipeline** with real data
4. **Add ideation canvas** to frontend
5. **Deploy to AWS EKS** for production testing

---

**Ready to test? Start with Step 1 and work through each scenario!** 🎉
