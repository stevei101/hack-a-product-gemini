"""Agent Pydantic schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from agentic_app.models.agent import AgentStatus


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    capabilities: Optional[List[str]] = Field(None)


class AgentCreate(AgentBase):
    """Agent creation schema."""
    pass


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    memory_context: Optional[str] = None


class Agent(AgentBase):
    """Agent response schema."""
    id: int
    status: AgentStatus
    current_task: Optional[str] = None
    memory_context: Optional[str] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None

    class Config:
        from_attributes = True
