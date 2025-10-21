"""Agent endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.core.database import get_db
from agentic_app.models.agent import AgentStatus
from agentic_app.schemas.agent import Agent, AgentCreate, AgentUpdate
from agentic_app.services.agent_service import agent_service

router = APIRouter()


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Create a new agent."""
    # Check if agent with same name already exists
    existing_agent = await agent_service.get_agent_by_name(db, agent_data.name)
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent with this name already exists"
        )
    
    return await agent_service.create_agent(db, agent_data)


@router.get("/", response_model=List[Agent])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Agent]:
    """Get all agents."""
    return await agent_service.get_agents(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Get an agent by ID."""
    agent = await agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Update an agent."""
    agent = await agent_service.update_agent(db, agent_id, agent_data)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete an agent."""
    success = await agent_service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )


@router.post("/{agent_id}/status", response_model=Agent)
async def update_agent_status(
    agent_id: int,
    status: AgentStatus,
    db: AsyncSession = Depends(get_db)
) -> Agent:
    """Update agent status."""
    agent = await agent_service.update_agent_status(db, agent_id, status)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.post("/{agent_id}/reason")
async def agent_reasoning(
    agent_id: int,
    task_description: str,
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get agent reasoning for a task."""
    agent = await agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    reasoning = await agent_service.reason_about_task(
        agent, task_description, context
    )
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "task_description": task_description,
        "reasoning": reasoning
    }


@router.post("/{agent_id}/plan")
async def plan_task_execution(
    agent_id: int,
    task_description: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get execution plan for a task."""
    agent = await agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    plan = await agent_service.plan_task_execution(agent, task_description)
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "task_description": task_description,
        "execution_plan": plan
    }
