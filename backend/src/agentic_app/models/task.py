"""Task model."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentic_app.core.database import Base


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(String(20), default=TaskStatus.PENDING)
    priority: Mapped[TaskPriority] = mapped_column(String(20), default=TaskPriority.MEDIUM)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=True)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subtasks: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="tasks")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"