"""
API Key schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class Permission(str, Enum):
    """Available API key permissions"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    NIM_ACCESS = "nim_access"
    RAG_ACCESS = "rag_access"
    TASK_MANAGEMENT = "task_management"
    AGENT_MANAGEMENT = "agent_management"


class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key"""
    name: str = Field(..., min_length=1, max_length=100, description="Name for the API key")
    description: Optional[str] = Field(None, max_length=500, description="Description of the API key")
    permissions: List[Permission] = Field(default=[Permission.READ], description="List of permissions")
    rate_limit: int = Field(default=1000, ge=1, le=100000, description="Rate limit (requests per hour)")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="Expiration in days (optional)")
    
    @validator('permissions')
    def validate_permissions(cls, v):
        if not v:
            raise ValueError("At least one permission is required")
        return v


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without sensitive data)"""
    id: int
    name: str
    description: Optional[str]
    key_prefix: str
    permissions: List[str]
    rate_limit: int
    is_active: bool
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ApiKeyWithSecret(BaseModel):
    """Schema for API key creation response (includes the actual key)"""
    id: int
    name: str
    description: Optional[str]
    key: str  # The actual API key (only shown once)
    key_prefix: str
    permissions: List[str]
    rate_limit: int
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: Optional[List[Permission]] = None
    rate_limit: Optional[int] = Field(None, ge=1, le=100000)
    is_active: Optional[bool] = None


class ApiKeyList(BaseModel):
    """Schema for listing API keys"""
    api_keys: List[ApiKeyResponse]
    total: int
    page: int
    per_page: int


class ApiKeyUsage(BaseModel):
    """Schema for API key usage statistics"""
    id: int
    name: str
    key_prefix: str
    usage_count: int
    last_used_at: Optional[datetime]
    rate_limit: int
    is_active: bool
    
    class Config:
        from_attributes = True
