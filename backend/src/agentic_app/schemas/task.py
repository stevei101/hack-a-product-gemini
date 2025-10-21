"""Task Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentic_app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    input_data: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskCreate(TaskBase):
    """Task creation schema."""
    agent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Task(TaskBase):
    """Task response schema."""
    id: int
    status: TaskStatus
    agent_id: Optional[int] = None
    output_data: Optional[str] = None
    subtasks: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
