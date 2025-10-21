"""Task service for managing tasks and their execution."""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.task import Task, TaskStatus
from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.schemas.task import TaskCreate, TaskUpdate
from agentic_app.services.agent_service import agent_service
from agentic_app.services.nim_service import nim_service

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing tasks and their execution."""

    def __init__(self):
        self.agent_service = agent_service
        self.nim_service = nim_service

    async def create_task(
        self, 
        db: AsyncSession, 
        task_data: TaskCreate
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            agent_id=task_data.agent_id,
            input_data=task_data.input_data,
            metadata=task_data.metadata,
            status=TaskStatus.PENDING,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Created task: {task.title}")
        return task

    async def get_task(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_tasks(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        agent_id: Optional[int] = None,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        """Get tasks with optional filtering."""
        query = select(Task)
        
        if agent_id:
            query = query.where(Task.agent_id == agent_id)
        if status:
            query = query.where(Task.status == status)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update_task(
        self, 
        db: AsyncSession, 
        task_id: int, 
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        task = await self.get_task(db, task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Updated task: {task.title}")
        return task

    async def delete_task(self, db: AsyncSession, task_id: int) -> bool:
        """Delete a task."""
        task = await self.get_task(db, task_id)
        if not task:
            return False

        await db.delete(task)
        await db.commit()
        
        logger.info(f"Deleted task: {task.title}")
        return True

    async def execute_task(
        self, 
        db: AsyncSession, 
        task_id: int
    ) -> Optional[dict]:
        """Execute a task using an agent."""
        task = await self.get_task(db, task_id)
        if not task:
            return None

        # Update task status to in progress
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        await db.commit()

        try:
            # Get the assigned agent
            agent = None
            if task.agent_id:
                agent = await self.agent_service.get_agent(db, task.agent_id)
                
                if agent:
                    # Update agent status to executing
                    await self.agent_service.update_agent_status(
                        db, task.agent_id, AgentStatus.EXECUTING
                    )

            # Execute the task
            result = await self._execute_task_logic(task, agent)

            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = result.get("output", "")
            task.subtasks = result.get("subtasks", [])

            # Update agent status back to idle
            if agent:
                await self.agent_service.update_agent_status(
                    db, task.agent_id, AgentStatus.IDLE
                )

            await db.commit()

            logger.info(f"Successfully executed task: {task.title}")
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result
            }

        except Exception as e:
            # Handle task execution error
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()

            # Update agent status back to idle
            if task.agent_id:
                await self.agent_service.update_agent_status(
                    db, task.agent_id, AgentStatus.IDLE
                )

            await db.commit()

            logger.error(f"Task execution failed: {task.title} - {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }

    async def _execute_task_logic(
        self, 
        task: Task, 
        agent: Optional[Agent]
    ) -> dict:
        """Execute the actual task logic using agent reasoning."""
        try:
            # Prepare the task execution prompt
            system_prompt = f"""You are an intelligent agent executing a task.
            
Task Title: {task.title}
Task Description: {task.description}
Priority: {task.priority}
Input Data: {task.input_data or "None"}

Please execute this task and provide:
1. A detailed output/result
2. Any subtasks that were completed
3. Any relevant metadata about the execution

Be thorough and provide actionable results."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Execute this task: {task.description}"}
            ]

            # Use NVIDIA NIM to execute the task
            response = await self.nim_service.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            # Parse the response to extract structured information
            # This is a simplified version - in practice, you'd want more sophisticated parsing
            subtasks = []
            if "subtasks:" in response.lower():
                # Extract subtasks if mentioned
                lines = response.split('\n')
                for line in lines:
                    if line.strip().startswith('-') or line.strip().startswith('*'):
                        subtasks.append(line.strip()[1:].strip())

            return {
                "output": response,
                "subtasks": subtasks,
                "metadata": {
                    "execution_time": datetime.utcnow().isoformat(),
                    "agent_id": agent.id if agent else None,
                    "agent_name": agent.name if agent else None,
                }
            }

        except Exception as e:
            logger.error(f"Error in task execution logic: {e}")
            raise


# Global instance
task_service = TaskService()
