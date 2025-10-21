"""Project model for the Product Mindset application."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agentic_app.core.database import Base


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class Project(Base):
    """Project model for organizing ideas, goals, features, and tasks."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(String(20), default=ProjectStatus.ACTIVE)
    
    # Project metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")
    ideas: Mapped[List["Idea"]] = relationship("Idea", back_populates="project")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class IdeaType(str, Enum):
    """Idea type enumeration."""
    IDEA = "idea"
    GOAL = "goal"
    FEATURE = "feature"
    TASK = "task"


class IdeaStatus(str, Enum):
    """Idea status enumeration."""
    BRAINSTORM = "brainstorm"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Idea(Base):
    """Idea model for the ideation canvas."""

    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[IdeaType] = mapped_column(String(20), default=IdeaType.IDEA)
    status: Mapped[IdeaStatus] = mapped_column(String(20), default=IdeaStatus.BRAINSTORM)
    
    # Project relationship
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    
    # Idea metadata
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="ideas")

    def __repr__(self) -> str:
        return f"<Idea(id={self.id}, title='{self.title}', type='{self.type}', status='{self.status}')>"
