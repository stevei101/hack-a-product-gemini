"""RAG (Retrieval-Augmented Generation) service for semantic search and context enhancement."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.task import Task
from agentic_app.services.nim_service import nim_service

logger = logging.getLogger(__name__)


class RAGService:
    """Service for Retrieval-Augmented Generation with semantic search."""

    def __init__(self):
        self.nim_service = nim_service
        self.similarity_threshold = 0.3
        self.max_retrieved_items = 3

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the given text using NVIDIA NIM."""
        try:
            return await self.nim_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec_a = np.array(a)
            vec_b = np.array(b)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec_a, vec_b)
            norm_a = np.linalg.norm(vec_a)
            norm_b = np.linalg.norm(vec_b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return dot_product / (norm_a * norm_b)
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    async def store_embedding(
        self, 
        db: AsyncSession, 
        entity_id: int, 
        entity_type: str, 
        text: str
    ) -> bool:
        """Store embedding for an entity (task, idea, etc.)."""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text)
            
            # Store in database (simplified - in production, use a proper vector database)
            embedding_key = f"{entity_type}:{entity_id}:embedding"
            embedding_data = {
                "embedding": embedding,
                "text": text,
                "entity_type": entity_type,
                "entity_id": entity_id
            }
            
            # For now, we'll store in the task's metadata field
            # In production, use a proper vector database like ChromaDB or Pinecone
            if entity_type == "task":
                task = await db.get(Task, entity_id)
                if task:
                    if not task.metadata:
                        task.metadata = {}
                    task.metadata[embedding_key] = embedding_data
                    await db.commit()
                    
            logger.info(f"Stored embedding for {entity_type}:{entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False

    async def retrieve_relevant_context(
        self, 
        db: AsyncSession, 
        query: str, 
        entity_type: str = "task"
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context based on semantic similarity."""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Get all entities of the specified type
            if entity_type == "task":
                from sqlalchemy import select
                result = await db.execute(select(Task))
                entities = result.scalars().all()
            else:
                entities = []
            
            relevant_items = []
            
            for entity in entities:
                if entity.metadata:
                    embedding_key = f"{entity_type}:{entity.id}:embedding"
                    if embedding_key in entity.metadata:
                        stored_embedding = entity.metadata[embedding_key]["embedding"]
                        text = entity.metadata[embedding_key]["text"]
                        
                        # Calculate similarity
                        similarity = self.cosine_similarity(query_embedding, stored_embedding)
                        
                        if similarity > self.similarity_threshold:
                            relevant_items.append({
                                "entity_id": entity.id,
                                "entity_type": entity_type,
                                "text": text,
                                "similarity": similarity,
                                "title": getattr(entity, 'title', 'Unknown'),
                                "description": getattr(entity, 'description', '')
                            })
            
            # Sort by similarity and return top items
            relevant_items.sort(key=lambda x: x["similarity"], reverse=True)
            return relevant_items[:self.max_retrieved_items]
            
        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            return []

    async def enhance_prompt_with_context(
        self, 
        db: AsyncSession, 
        original_prompt: str, 
        entity_type: str = "task"
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Enhance the original prompt with retrieved context."""
        try:
            # Retrieve relevant context
            relevant_context = await self.retrieve_relevant_context(db, original_prompt, entity_type)
            
            if not relevant_context:
                return original_prompt, []
            
            # Build enhanced prompt
            enhanced_prompt = original_prompt
            
            if relevant_context:
                enhanced_prompt += "\n\nRelevant Context from Project History:\n"
                for i, item in enumerate(relevant_context, 1):
                    enhanced_prompt += f"{i}. {item['title']}: {item['text']}\n"
                
                enhanced_prompt += "\nPlease reference this context in your response and provide relevant suggestions."
            
            return enhanced_prompt, relevant_context
            
        except Exception as e:
            logger.error(f"Error enhancing prompt with context: {e}")
            return original_prompt, []

    async def generate_rag_response(
        self, 
        db: AsyncSession, 
        user_message: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate a response using RAG (Retrieval-Augmented Generation)."""
        try:
            # Enhance prompt with relevant context
            enhanced_prompt, retrieved_context = await self.enhance_prompt_with_context(
                db, user_message, "task"
            )
            
            # Build conversation messages
            messages = conversation_history or []
            messages.append({"role": "user", "content": enhanced_prompt})
            
            # Generate response using NVIDIA NIM
            response = await self.nim_service.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=4096
            )
            
            return {
                "response": response,
                "retrieved_context": retrieved_context,
                "rag_active": len(retrieved_context) > 0,
                "context_count": len(retrieved_context)
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return {
                "response": "I apologize, but I encountered an error while processing your request.",
                "retrieved_context": [],
                "rag_active": False,
                "context_count": 0,
                "error": str(e)
            }

    async def get_embedding_status(self, db: AsyncSession, entity_type: str = "task") -> Dict[str, Any]:
        """Get the status of embeddings for all entities."""
        try:
            if entity_type == "task":
                from sqlalchemy import select
                result = await db.execute(select(Task))
                entities = result.scalars().all()
            else:
                entities = []
            
            total_entities = len(entities)
            embedded_entities = 0
            embedding_dimensions = 0
            
            for entity in entities:
                if entity.metadata:
                    embedding_key = f"{entity_type}:{entity.id}:embedding"
                    if embedding_key in entity.metadata:
                        embedded_entities += 1
                        if embedding_dimensions == 0:
                            embedding_data = entity.metadata[embedding_key]
                            if "embedding" in embedding_data:
                                embedding_dimensions = len(embedding_data["embedding"])
            
            return {
                "total_entities": total_entities,
                "embedded_entities": embedded_entities,
                "embedding_percentage": (embedded_entities / total_entities * 100) if total_entities > 0 else 0,
                "embedding_dimensions": embedding_dimensions,
                "similarity_threshold": self.similarity_threshold,
                "max_retrieved_items": self.max_retrieved_items
            }
            
        except Exception as e:
            logger.error(f"Error getting embedding status: {e}")
            return {
                "total_entities": 0,
                "embedded_entities": 0,
                "embedding_percentage": 0,
                "embedding_dimensions": 0,
                "error": str(e)
            }


# Global instance
rag_service = RAGService()
