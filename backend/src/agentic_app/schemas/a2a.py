"""A2A Protocol Pydantic schemas."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_app.models.agent_message import MessageType


class A2AMessageBase(BaseModel):
    """Base A2A message schema."""
    from_agent_id: int
    to_agent_id: Optional[int] = None  # None for broadcast
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False
    parent_message_id: Optional[uuid.UUID] = None


class A2AMessageCreate(A2AMessageBase):
    """A2A message creation schema."""
    conversation_id: Optional[uuid.UUID] = None  # Will be generated if not provided


class A2AMessage(A2AMessageBase):
    """A2A message response schema."""
    id: int
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentHandoffRequest(BaseModel):
    """Agent handoff request."""
    from_agent_id: int
    to_agent_id: int
    task_id: int
    context: str
    reason: str
    capabilities_needed: List[str] = Field(default_factory=list)


class AgentHelpRequest(BaseModel):
    """Agent requesting help from another agent."""
    requesting_agent_id: int
    target_capability: str
    query: str
    context: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, critical


class AgentBroadcast(BaseModel):
    """Broadcast message to all agents."""
    from_agent_id: int
    message: str
    metadata: Optional[Dict[str, Any]] = None
    requires_acknowledgment: bool = False


class ConversationStatus(str, Enum):
    """Conversation status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class AgentConversationCreate(BaseModel):
    """Conversation creation schema."""
    task_id: Optional[int] = None
    participating_agents: List[int]
    context: Optional[str] = None


class AgentConversationResponse(BaseModel):
    """Conversation response schema."""
    id: int
    conversation_id: uuid.UUID
    task_id: Optional[int] = None
    participating_agents: List[int]
    status: str
    context: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    result_summary: Optional[str] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Response after sending a message."""
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    status: str = "sent"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentDiscoveryRequest(BaseModel):
    """Request to discover agents with specific capabilities."""
    required_capabilities: List[str]
    exclude_agents: List[int] = Field(default_factory=list)
    max_results: int = 10


class AgentDiscoveryResponse(BaseModel):
    """Response with discovered agents."""
    agents: List[Dict[str, Any]]
    count: int


class CoordinationTask(BaseModel):
    """Multi-agent coordination task."""
    task_id: int
    coordinator_agent_id: int
    subtasks: List[Dict[str, Any]] = Field(default_factory=list)
    coordination_strategy: str = "parallel"  # parallel, sequential, adaptive


class CoordinationResult(BaseModel):
    """Result of multi-agent coordination."""
    task_id: int
    conversation_id: uuid.UUID
    status: str
    participating_agents: List[int]
    subtask_results: List[Dict[str, Any]]
    final_result: Optional[str] = None
    completed_at: Optional[datetime] = None

