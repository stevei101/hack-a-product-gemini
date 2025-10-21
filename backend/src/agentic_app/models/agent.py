"""Agent model."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from agentic_app.core.database import Base


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    ERROR = "error"
    LEARNING = "learning"


class Agent(Base):
    """Agent model."""

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

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', status='{self.status}')>"
