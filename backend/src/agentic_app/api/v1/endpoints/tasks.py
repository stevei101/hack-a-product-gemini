"""Task endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.core.database import get_db
from agentic_app.models.task import TaskStatus
from agentic_app.schemas.task import Task, TaskCreate, TaskUpdate
from agentic_app.services.task_service import task_service

router = APIRouter()


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
) -> Task:
    """Create a new task."""
    return await task_service.create_task(db, task_data)


@router.get("/", response_model=List[Task])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    db: AsyncSession = Depends(get_db)
) -> List[Task]:
    """Get tasks with optional filtering."""
    return await task_service.get_tasks(
        db, skip=skip, limit=limit, agent_id=agent_id, status=status
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> Task:
    """Get a task by ID."""
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
) -> Task:
    """Update a task."""
    task = await task_service.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a task."""
    success = await task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.post("/{task_id}/execute")
async def execute_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Execute a task using an agent."""
    result = await task_service.execute_task(db, task_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return result
