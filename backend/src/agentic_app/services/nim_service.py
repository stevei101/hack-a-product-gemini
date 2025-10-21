"""NVIDIA NIM service integration."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from agentic_app.core.config import settings

logger = logging.getLogger(__name__)


class NimMessage(BaseModel):
    """NIM message model."""
    role: str
    content: str


class NimRequest(BaseModel):
    """NIM API request model."""
    model: str
    messages: List[NimMessage]
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 0.9
    stream: Optional[bool] = False
    parameters: Optional[Dict[str, Any]] = None


class NimResponse(BaseModel):
    """NIM API response model."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class NimService:
    """NVIDIA NIM service for LLM inference and embeddings."""

    def __init__(self):
        self.base_url = settings.NIM_BASE_URL
        self.api_key = settings.NIM_API_KEY
        self.model_name = "nvidia/llama-3_1-nemotron-nano-8b-v1"  # Correct hackathon model name
        self.embedding_model = "nvidia/nv-embedqa-e5-v5"  # Correct embedding model
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate a response using the NVIDIA NIM LLM."""
        try:
            # Add Nemotron-specific system parameter for hackathon compliance
            nemotron_messages = [
                {"role": "system", "content": "detailed thinking off"}  # Nemotron-specific parameter
            ] + messages
            
            request_data = NimRequest(
                model=self.model_name,
                messages=[NimMessage(**msg) for msg in nemotron_messages],
                max_tokens=max_tokens or 4096,
                temperature=temperature or 0.7,
                top_p=kwargs.get('top_p', 0.95),
                **kwargs
            )

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=request_data.model_dump(exclude_none=True)
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("choices") and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("No response generated from NIM service")

        except httpx.HTTPError as e:
            logger.error(f"NIM HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"NIM service error: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the given text."""
        try:
            request_data = {
                "model": self.embedding_model,
                "input": text,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=request_data
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("data") and len(result["data"]) > 0:
                    return result["data"][0]["embedding"]
                else:
                    raise ValueError("No embedding generated from NIM service")

        except httpx.HTTPError as e:
            logger.error(f"NIM embedding HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"NIM embedding service error: {e}")
            raise

    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        tasks = [self.generate_embedding(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def health_check(self) -> bool:
        """Check if the NIM service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"NIM health check failed: {e}")
            return False


# Global instance
nim_service = NimService()
