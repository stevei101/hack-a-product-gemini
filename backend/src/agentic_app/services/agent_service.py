"""Agent service for managing agents and their reasoning capabilities."""

import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.schemas.agent import AgentCreate, AgentUpdate
from agentic_app.services.nim_service import nim_service

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing agents and their reasoning capabilities."""

    def __init__(self):
        self.nim_service = nim_service

    async def create_agent(
        self, 
        db: AsyncSession, 
        agent_data: AgentCreate
    ) -> Agent:
        """Create a new agent."""
        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            capabilities=agent_data.capabilities,
            status=AgentStatus.IDLE,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Created agent: {agent.name}")
        return agent

    async def get_agent(self, db: AsyncSession, agent_id: int) -> Optional[Agent]:
        """Get an agent by ID."""
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_agent_by_name(self, db: AsyncSession, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        result = await db.execute(select(Agent).where(Agent.name == name))
        return result.scalar_one_or_none()

    async def get_agents(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Agent]:
        """Get all agents with pagination."""
        result = await db.execute(
            select(Agent).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update_agent(
        self, 
        db: AsyncSession, 
        agent_id: int, 
        agent_data: AgentUpdate
    ) -> Optional[Agent]:
        """Update an agent."""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            return None

        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)

        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Updated agent: {agent.name}")
        return agent

    async def delete_agent(self, db: AsyncSession, agent_id: int) -> bool:
        """Delete an agent."""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            return False

        await db.delete(agent)
        await db.commit()
        
        logger.info(f"Deleted agent: {agent.name}")
        return True

    async def update_agent_status(
        self, 
        db: AsyncSession, 
        agent_id: int, 
        status: AgentStatus
    ) -> Optional[Agent]:
        """Update agent status."""
        agent = await self.get_agent(db, agent_id)
        if not agent:
            return None

        agent.status = status
        await db.commit()
        await db.refresh(agent)
        
        return agent

    async def reason_about_task(
        self, 
        agent: Agent, 
        task_description: str, 
        context: Optional[str] = None
    ) -> str:
        """Use the agent's reasoning capabilities to analyze a task."""
        try:
            # Prepare the reasoning prompt
            system_prompt = f"""You are an intelligent agent named {agent.name}.
            
Your capabilities include: {', '.join(agent.capabilities or [])}
Your current status is: {agent.status}

Please analyze the following task and provide your reasoning about how to approach it.
Consider your capabilities, current context, and any relevant information.

Current context: {context or "No additional context provided"}

Task to analyze: {task_description}

Provide a detailed reasoning about:
1. How you would approach this task
2. What steps you would take
3. Any challenges or considerations
4. Your confidence level in completing this task

Be specific and actionable in your reasoning."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
            ]

            # Generate reasoning using NVIDIA NIM
            reasoning = await self.nim_service.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            # Update agent's memory context
            agent.memory_context = reasoning
            
            logger.info(f"Agent {agent.name} generated reasoning for task")
            return reasoning

        except Exception as e:
            logger.error(f"Error in agent reasoning: {e}")
            raise

    async def plan_task_execution(
        self, 
        agent: Agent, 
        task_description: str
    ) -> List[str]:
        """Plan the execution steps for a task."""
        try:
            system_prompt = f"""You are an intelligent agent planning task execution.
            
Agent: {agent.name}
Capabilities: {', '.join(agent.capabilities or [])}

Break down the following task into specific, actionable steps.
Return only a JSON array of step descriptions, no additional text.

Task: {task_description}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
            ]

            # Generate execution plan
            plan_response = await self.nim_service.generate_response(
                messages=messages,
                temperature=0.5,
                max_tokens=500
            )

            # Parse the response as a JSON array
            import json
            try:
                steps = json.loads(plan_response)
                if isinstance(steps, list):
                    return steps
                else:
                    return [str(steps)]
            except json.JSONDecodeError:
                # If not valid JSON, split by lines
                return [step.strip() for step in plan_response.split('\n') if step.strip()]

        except Exception as e:
            logger.error(f"Error in task planning: {e}")
            return [f"Error planning task: {str(e)}"]


# Global instance
agent_service = AgentService()
