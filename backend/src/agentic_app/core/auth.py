from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
import os

from agentic_app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(credentials: str = Depends(api_key_header)):
    """Verify the API key from the request header."""
    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="API key not configured on server"
        )
    
    if not credentials or credentials != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    return credentials