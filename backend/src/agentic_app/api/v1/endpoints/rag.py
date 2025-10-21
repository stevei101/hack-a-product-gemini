"""RAG (Retrieval-Augmented Generation) endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.core.database import get_db
from agentic_app.services.rag_service import rag_service

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request with RAG support."""
    message: str
    project_id: Optional[int] = None
    conversation_history: Optional[List[dict]] = None


class EmbeddingStatusResponse(BaseModel):
    """Response model for embedding status."""
    total_entities: int
    embedded_entities: int
    embedding_percentage: float
    embedding_dimensions: int
    similarity_threshold: float
    max_retrieved_items: int


class RAGResponse(BaseModel):
    """Response model for RAG chat."""
    response: str
    retrieved_context: List[dict]
    rag_active: bool
    context_count: int
    error: Optional[str] = None


@router.post("/chat", response_model=RAGResponse)
async def rag_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> RAGResponse:
    """Chat with AI using RAG (Retrieval-Augmented Generation)."""
    try:
        result = await rag_service.generate_rag_response(
            db=db,
            user_message=request.message,
            conversation_history=request.conversation_history or []
        )
        
        return RAGResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in RAG chat: {str(e)}"
        )


@router.post("/embeddings/{entity_type}/{entity_id}")
async def generate_embedding(
    entity_type: str,
    entity_id: int,
    text: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Generate and store embedding for an entity."""
    try:
        success = await rag_service.store_embedding(
            db=db,
            entity_id=entity_id,
            entity_type=entity_type,
            text=text
        )
        
        if success:
            return {
                "success": True,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "message": "Embedding generated and stored successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate or store embedding"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating embedding: {str(e)}"
        )


@router.get("/embeddings/status", response_model=EmbeddingStatusResponse)
async def get_embedding_status(
    entity_type: str = "task",
    db: AsyncSession = Depends(get_db)
) -> EmbeddingStatusResponse:
    """Get the status of embeddings for all entities."""
    try:
        status_data = await rag_service.get_embedding_status(db, entity_type)
        return EmbeddingStatusResponse(**status_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting embedding status: {str(e)}"
        )


@router.post("/retrieve")
async def retrieve_context(
    query: str,
    entity_type: str = "task",
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Retrieve relevant context based on semantic similarity."""
    try:
        relevant_context = await rag_service.retrieve_relevant_context(
            db=db,
            query=query,
            entity_type=entity_type
        )
        
        return {
            "query": query,
            "entity_type": entity_type,
            "relevant_context": relevant_context,
            "context_count": len(relevant_context)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving context: {str(e)}"
        )


@router.post("/similarity")
async def calculate_similarity(
    text1: str,
    text2: str
) -> dict:
    """Calculate cosine similarity between two texts."""
    try:
        # Generate embeddings for both texts
        embedding1 = await rag_service.generate_embedding(text1)
        embedding2 = await rag_service.generate_embedding(text2)
        
        # Calculate similarity
        similarity = rag_service.cosine_similarity(embedding1, embedding2)
        
        return {
            "text1": text1,
            "text2": text2,
            "similarity": similarity,
            "embedding_dimensions": len(embedding1)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating similarity: {str(e)}"
        )
