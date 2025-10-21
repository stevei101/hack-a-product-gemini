"""NVIDIA NIM endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from agentic_app.services.nim_service import nim_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[dict]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class EmbeddingRequest(BaseModel):
    """Embedding request model."""
    text: str


class BatchEmbeddingRequest(BaseModel):
    """Batch embedding request model."""
    texts: List[str]


@router.post("/chat")
async def chat_completion(request: ChatRequest) -> dict:
    """Generate a chat completion using NVIDIA NIM."""
    try:
        response = await nim_service.generate_response(
            messages=request.messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "response": response,
            "model": nim_service.model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@router.post("/embeddings")
async def generate_embedding(request: EmbeddingRequest) -> dict:
    """Generate embeddings for text using NVIDIA NIM."""
    try:
        embedding = await nim_service.generate_embedding(request.text)
        
        return {
            "embedding": embedding,
            "model": nim_service.embedding_model,
            "dimension": len(embedding)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embedding: {str(e)}"
        )


@router.post("/embeddings/batch")
async def batch_generate_embeddings(request: BatchEmbeddingRequest) -> dict:
    """Generate embeddings for multiple texts."""
    try:
        embeddings = await nim_service.batch_generate_embeddings(request.texts)
        
        return {
            "embeddings": embeddings,
            "model": nim_service.embedding_model,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embeddings: {str(e)}"
        )


@router.get("/health")
async def nim_health_check() -> dict:
    """Check NVIDIA NIM service health."""
    is_healthy = await nim_service.health_check()
    
    return {
        "healthy": is_healthy,
        "service": "NVIDIA NIM",
        "model": nim_service.model_name,
        "embedding_model": nim_service.embedding_model
    }


@router.get("/models")
async def list_models() -> dict:
    """List available NIM models."""
    return {
        "llm_model": nim_service.model_name,
        "embedding_model": nim_service.embedding_model,
        "base_url": nim_service.base_url
    }
