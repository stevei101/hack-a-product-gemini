"""Agent message model for A2A communication."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentic_app.core.database import Base


class MessageType(str, Enum):
    """A2A message types."""
    REQUEST = "request"          # Agent requests help
    RESPONSE = "response"        # Agent responds to request
    HANDOFF = "handoff"         # Transfer task to another agent
    BROADCAST = "broadcast"      # Announce to all agents
    COORDINATE = "coordinate"    # Coordination message
    DELEGATE = "delegate"        # Delegate subtask


class AgentMessage(Base):
    """Agent-to-Agent message model."""

    __tablename__ = "agent_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, index=True)
    from_agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), index=True)
    to_agent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("agents.id"), nullable=True, index=True
    )
    message_type: Mapped[MessageType] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    requires_response: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_message_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    from_agent: Mapped["Agent"] = relationship(
        "Agent",
        foreign_keys=[from_agent_id],
        back_populates="sent_messages"
    )
    to_agent: Mapped[Optional["Agent"]] = relationship(
        "Agent",
        foreign_keys=[to_agent_id],
        back_populates="received_messages"
    )

    def __repr__(self) -> str:
        return f"<AgentMessage(id={self.id}, from={self.from_agent_id}, to={self.to_agent_id}, type='{self.message_type}')>"


class AgentConversation(Base):
    """Agent conversation thread for multi-agent coordination."""

    __tablename__ = "agent_conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), unique=True, index=True
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )
    participating_agents: Mapped[list[int]] = mapped_column(
        JSONB
    )  # Array of agent IDs
    status: Mapped[str] = mapped_column(String(50), default="active")
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    result_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<AgentConversation(id={self.id}, agents={len(self.participating_agents)}, status='{self.status}')>"


class AgentCapabilityRegistry(Base):
    """Registry of agent capabilities for discovery and matching."""

    __tablename__ = "agent_capabilities_registry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), index=True)
    capability_name: Mapped[str] = mapped_column(String(100), index=True)
    capability_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    agent: Mapped["Agent"] = relationship("Agent", back_populates="capability_registry")

    def __repr__(self) -> str:
        return f"<AgentCapabilityRegistry(agent_id={self.agent_id}, capability='{self.capability_name}')>"

