#!/usr/bin/env python3
"""Simplified test server for the agentic application."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Simple models for testing
class HealthResponse(BaseModel):
    status: str
    message: str

class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 100

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    print("🚀 Starting The Product Mindset - Agentic Application")
    print("📡 Backend server starting...")
    yield
    print("🛑 Shutting down server...")

# Create FastAPI app
app = FastAPI(
    title="The Product Mindset",
    description="AI-powered agentic workspace for creators and developers",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "The Product Mindset - Agentic Application API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="The Product Mindset is running correctly"
    )

@app.get("/api/v1/nim/health", response_model=dict)
async def nim_health():
    """NVIDIA NIM health check."""
    return {
        "status": "nim_available",
        "model": "nvidia/llama-3_1-nemotron-nano-8b-v1",
        "embedding_model": "nvidia/nv-embedqa-e5-v5",
        "message": "NVIDIA NIM integration ready (API key required for full functionality)"
    }

@app.post("/api/v1/nim/chat", response_model=ChatResponse)
async def nim_chat(request: ChatRequest):
    """Chat with NVIDIA NIM (mock response for testing)."""
    return ChatResponse(
        response=f"Hello! I'm the NVIDIA NIM model (llama-3_1-nemotron-nano-8b-v1). You said: '{request.message}'. This is a mock response for testing.",
        model="nvidia/llama-3_1-nemotron-nano-8b-v1",
        tokens_used=50
    )

@app.get("/api/v1/rag/embeddings/status", response_model=dict)
async def rag_status():
    """RAG embedding status."""
    return {
        "total_entities": 0,
        "embedded_entities": 0,
        "embedding_percentage": 0.0,
        "embedding_dimensions": 1024,
        "similarity_threshold": 0.3,
        "max_retrieved_items": 3,
        "message": "RAG system ready (no entities embedded yet)"
    }

@app.post("/api/v1/rag/chat", response_model=dict)
async def rag_chat(request: ChatRequest):
    """RAG-powered chat (mock response for testing)."""
    return {
        "response": f"I'm using RAG (Retrieval-Augmented Generation) to respond to: '{request.message}'. This is a mock response for testing.",
        "retrieved_context": [],
        "rag_active": False,
        "context_count": 0
    }

@app.get("/api/v1/agents", response_model=dict)
async def list_agents():
    """List agents (mock response for testing)."""
    return {
        "agents": [
            {
                "id": 1,
                "name": "Research Agent",
                "description": "An agent specialized in research tasks",
                "status": "idle",
                "capabilities": ["research", "analysis", "summarization"]
            },
            {
                "id": 2,
                "name": "Planning Agent", 
                "description": "An agent specialized in planning and organization",
                "status": "idle",
                "capabilities": ["planning", "organization", "task_management"]
            }
        ],
        "total": 2
    }

@app.get("/api/v1/tasks", response_model=dict)
async def list_tasks():
    """List tasks (mock response for testing)."""
    return {
        "tasks": [
            {
                "id": 1,
                "title": "Market Research",
                "description": "Research the latest trends in AI technology",
                "status": "pending",
                "priority": "high",
                "agent_id": 1
            },
            {
                "id": 2,
                "title": "Project Planning",
                "description": "Create a comprehensive project plan",
                "status": "in_progress",
                "priority": "medium",
                "agent_id": 2
            }
        ],
        "total": 2
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting The Product Mindset - Test Server")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("\n🎯 Ready for testing!")
    
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
