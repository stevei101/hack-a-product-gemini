"""Agent Pydantic schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_app.models.agent import AgentRole, AgentStatus


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    capabilities: Optional[List[str]] = Field(None)
    role: Optional[AgentRole] = None


class AgentCreate(AgentBase):
    """Agent creation schema."""
    pass


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[AgentStatus] = None
    role: Optional[AgentRole] = None
    capabilities: Optional[List[str]] = None
    memory_context: Optional[str] = None
    communication_endpoint: Optional[str] = None
    trusted_agents: Optional[List[int]] = None


class Agent(AgentBase):
    """Agent response schema."""
    id: int
    status: AgentStatus
    current_task: Optional[str] = None
    memory_context: Optional[str] = None
    created_at: datetime
    last_active_at: Optional[datetime] = None
    # A2A fields
    communication_endpoint: Optional[str] = None
    trusted_agents: Optional[List[int]] = None
    collaboration_history: Optional[Dict] = None
    max_concurrent_collaborations: int = 3

    class Config:
        from_attributes = True
