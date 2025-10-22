"""Agent model."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentic_app.core.database import Base


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"
    LEARNING = "learning"


class AgentRole(str, Enum):
    """Agent role in multi-agent system."""
    COORDINATOR = "coordinator"    # Orchestrates multi-agent tasks
    SPECIALIST = "specialist"      # Domain-specific expert
    REVIEWER = "reviewer"          # Reviews and validates work
    EXECUTOR = "executor"          # General task execution
    RESEARCHER = "researcher"      # Information gathering


class Agent(Base):
    """Agent model with A2A protocol support."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[AgentStatus] = mapped_column(String(20), default=AgentStatus.IDLE)
    current_task: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    capabilities: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    memory_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # A2A Protocol fields
    role: Mapped[Optional[AgentRole]] = mapped_column(String(20), nullable=True)
    communication_endpoint: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    trusted_agents: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    collaboration_history: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    max_concurrent_collaborations: Mapped[int] = mapped_column(Integer, default=3)
    
    # Relationships for A2A
    sent_messages: Mapped[List["AgentMessage"]] = relationship(
        "AgentMessage",
        foreign_keys="AgentMessage.from_agent_id",
        back_populates="from_agent",
        lazy="dynamic"
    )
    received_messages: Mapped[List["AgentMessage"]] = relationship(
        "AgentMessage",
        foreign_keys="AgentMessage.to_agent_id",
        back_populates="to_agent",
        lazy="dynamic"
    )
    capability_registry: Mapped[List["AgentCapabilityRegistry"]] = relationship(
        "AgentCapabilityRegistry",
        back_populates="agent",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', role='{self.role}', status='{self.status}')>"
