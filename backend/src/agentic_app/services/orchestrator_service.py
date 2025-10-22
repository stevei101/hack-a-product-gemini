"""Multi-Agent Orchestrator Service."""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.models.task import Task, TaskStatus
from agentic_app.schemas.a2a import A2AMessageCreate, CoordinationTask, MessageType
from agentic_app.services.a2a_service import a2a_service
from agentic_app.services.agent_service import agent_service
from agentic_app.services.nim_service import nim_service

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orchestrates multi-agent collaboration for complex tasks."""

    def __init__(self):
        """Initialize orchestrator."""
        self.a2a_service = a2a_service
        self.agent_service = agent_service
        self.nim_service = nim_service

    async def coordinate_task(
        self, db: AsyncSession, task_id: int, coordinator_agent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to complete a complex task.
        
        Args:
            db: Database session
            task_id: ID of the task to coordinate
            coordinator_agent_id: Optional specific coordinator agent
            
        Returns:
            Dictionary with coordination results
        """
        try:
            # Get task
            task = await db.get(Task, task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            await db.commit()

            logger.info(f"Starting multi-agent coordination for task {task_id}")

            # 1. Decompose task into subtasks
            subtasks = await self._decompose_task(task)
            logger.info(f"Task decomposed into {len(subtasks)} subtasks")

            # 2. Find or assign coordinator agent
            coordinator = await self._get_coordinator_agent(
                db, coordinator_agent_id
            )
            if not coordinator:
                logger.warning("No coordinator agent available, using direct assignment")

            # 3. Match subtasks to agent capabilities
            assignments = await self._assign_subtasks_to_agents(db, subtasks)
            logger.info(f"Assigned {len(assignments)} subtasks to agents")

            # 4. Create conversation thread for coordination
            participating_agents = [a["agent_id"] for a in assignments]
            if coordinator:
                participating_agents.insert(0, coordinator.id)

            conversation = await self.a2a_service.create_conversation(
                db, task_id, participating_agents
            )

            # 5. Execute coordinated workflow
            results = await self._execute_coordinated_workflow(
                db, task, assignments, conversation.conversation_id, coordinator
            )

            # 6. Aggregate results
            final_result = await self._aggregate_results(results)

            # 7. Update task with final result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = final_result["output"]
            await db.commit()

            logger.info(f"Multi-agent coordination completed for task {task_id}")

            return {
                "task_id": task_id,
                "conversation_id": str(conversation.conversation_id),
                "coordinator": coordinator.name if coordinator else "none",
                "participating_agents": len(participating_agents),
                "subtasks_completed": len(results),
                "final_result": final_result,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error in multi-agent coordination: {e}")
            # Update task status to failed
            if task:
                task.status = TaskStatus.FAILED
                await db.commit()
            raise

    async def _decompose_task(self, task: Task) -> List[Dict[str, Any]]:
        """Decompose complex task using NIM reasoning."""
        try:
            prompt = f"""Decompose the following task into specific, actionable subtasks.
            
Task Title: {task.title}
Task Description: {task.description}
Priority: {task.priority}

Return a JSON array of subtasks. Each subtask should have:
- "description": Clear description of what needs to be done
- "required_capabilities": List of capabilities needed (e.g., ["research", "analysis", "writing"])
- "dependencies": List of indices of prerequisite subtasks (empty array if none)
- "estimated_complexity": "low", "medium", or "high"

Example format:
[
  {{
    "description": "Research the topic",
    "required_capabilities": ["research", "data_gathering"],
    "dependencies": [],
    "estimated_complexity": "medium"
  }},
  {{
    "description": "Analyze findings",
    "required_capabilities": ["analysis"],
    "dependencies": [0],
    "estimated_complexity": "high"
  }}
]

Important: Return ONLY the JSON array, no additional text."""

            messages = [
                {
                    "role": "system",
                    "content": "You are a task decomposition expert. Respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ]

            response = await self.nim_service.generate_response(
                messages=messages, temperature=0.3, max_tokens=1500
            )

            # Parse JSON response
            try:
                # Clean up response (remove markdown code blocks if present)
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()

                subtasks = json.loads(cleaned)
                if not isinstance(subtasks, list):
                    subtasks = [subtasks]

                return subtasks

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse subtasks JSON: {e}, using fallback")
                # Fallback: create a single subtask
                return [
                    {
                        "description": task.description,
                        "required_capabilities": ["general"],
                        "dependencies": [],
                        "estimated_complexity": "medium",
                    }
                ]

        except Exception as e:
            logger.error(f"Error decomposing task: {e}")
            # Fallback
            return [
                {
                    "description": task.description,
                    "required_capabilities": ["general"],
                    "dependencies": [],
                    "estimated_complexity": "medium",
                }
            ]

    async def _get_coordinator_agent(
        self, db: AsyncSession, preferred_id: Optional[int] = None
    ) -> Optional[Agent]:
        """Get or select a coordinator agent."""
        try:
            # If preferred coordinator specified, try to get it
            if preferred_id:
                agent = await agent_service.get_agent(db, preferred_id)
                if agent and agent.status != AgentStatus.ERROR:
                    return agent

            # Otherwise, find an agent with coordinator role
            from sqlalchemy import select
            from agentic_app.models.agent import AgentRole

            result = await db.execute(
                select(Agent).where(
                    Agent.role == AgentRole.COORDINATOR,
                    Agent.status != AgentStatus.ERROR,
                )
            )
            coordinator = result.scalar_one_or_none()

            return coordinator

        except Exception as e:
            logger.error(f"Error getting coordinator agent: {e}")
            return None

    async def _assign_subtasks_to_agents(
        self, db: AsyncSession, subtasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Match subtasks to agent capabilities."""
        assignments = []

        for idx, subtask in enumerate(subtasks):
            required_caps = subtask.get("required_capabilities", ["general"])

            # Find best agent for this subtask
            best_agent = None
            for capability in required_caps:
                agents = await self.a2a_service._find_agents_by_capability(
                    db, capability
                )
                if agents:
                    best_agent = await self.a2a_service._select_best_agent(agents)
                    break

            # If no specific agent found, get any available agent
            if not best_agent:
                from sqlalchemy import select

                result = await db.execute(
                    select(Agent).where(Agent.status == AgentStatus.IDLE).limit(1)
                )
                best_agent = result.scalar_one_or_none()

            if best_agent:
                assignments.append(
                    {
                        "subtask_index": idx,
                        "subtask": subtask,
                        "agent_id": best_agent.id,
                        "agent_name": best_agent.name,
                    }
                )
            else:
                logger.warning(f"No agent available for subtask {idx}")

        return assignments

    async def _execute_coordinated_workflow(
        self,
        db: AsyncSession,
        task: Task,
        assignments: List[Dict[str, Any]],
        conversation_id: uuid.UUID,
        coordinator: Optional[Agent],
    ) -> List[Dict[str, Any]]:
        """Execute subtasks in coordinated workflow."""
        results = []

        # Organize by dependencies
        completed = set()
        pending = assignments.copy()

        max_iterations = len(assignments) + 5  # Prevent infinite loops
        iteration = 0

        while pending and iteration < max_iterations:
            iteration += 1

            # Find subtasks ready to execute (dependencies met)
            ready_to_execute = []
            for assignment in pending:
                subtask = assignment["subtask"]
                dependencies = subtask.get("dependencies", [])

                # Check if all dependencies are completed
                if all(dep in completed for dep in dependencies):
                    ready_to_execute.append(assignment)

            if not ready_to_execute:
                logger.warning("No subtasks ready to execute, may have circular dependencies")
                break

            # Execute ready subtasks (in parallel if possible)
            tasks_to_execute = [
                self._execute_subtask(db, assignment, conversation_id, task)
                for assignment in ready_to_execute
            ]

            subtask_results = await asyncio.gather(*tasks_to_execute, return_exceptions=True)

            # Process results
            for i, result in enumerate(subtask_results):
                assignment = ready_to_execute[i]
                if isinstance(result, Exception):
                    logger.error(f"Subtask {assignment['subtask_index']} failed: {result}")
                    results.append(
                        {
                            "subtask_index": assignment["subtask_index"],
                            "agent_id": assignment["agent_id"],
                            "status": "failed",
                            "error": str(result),
                        }
                    )
                else:
                    results.append(result)
                    completed.add(assignment["subtask_index"])

                # Remove from pending
                pending.remove(assignment)

        if pending:
            logger.warning(f"{len(pending)} subtasks could not be completed")

        return results

    async def _execute_subtask(
        self,
        db: AsyncSession,
        assignment: Dict[str, Any],
        conversation_id: uuid.UUID,
        parent_task: Task,
    ) -> Dict[str, Any]:
        """Execute a single subtask."""
        try:
            agent_id = assignment["agent_id"]
            subtask = assignment["subtask"]

            # Get agent
            agent = await agent_service.get_agent(db, agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            # Update agent status
            await agent_service.update_agent_status(db, agent_id, AgentStatus.EXECUTING)

            # Execute subtask using agent reasoning
            prompt = f"""Execute the following subtask as part of a larger task:

Subtask: {subtask['description']}
Complexity: {subtask.get('estimated_complexity', 'medium')}
Parent Task: {parent_task.title}

Provide a detailed result of your work."""

            result_content = await self.agent_service.reason_about_task(
                agent, prompt, context=parent_task.description
            )

            # Update agent status back to idle
            await agent_service.update_agent_status(db, agent_id, AgentStatus.IDLE)

            logger.info(f"Subtask {assignment['subtask_index']} completed by Agent {agent_id}")

            return {
                "subtask_index": assignment["subtask_index"],
                "agent_id": agent_id,
                "agent_name": agent.name,
                "status": "completed",
                "result": result_content,
            }

        except Exception as e:
            logger.error(f"Error executing subtask: {e}")
            raise

    async def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple agents."""
        try:
            # Combine all successful results
            successful_results = [r for r in results if r.get("status") == "completed"]

            if not successful_results:
                return {"output": "No successful results", "metadata": {"success": False}}

            # Use NIM to synthesize final result
            combined_text = "\n\n".join(
                [
                    f"Agent {r['agent_name']} (Subtask {r['subtask_index']}): {r['result']}"
                    for r in successful_results
                ]
            )

            prompt = f"""Synthesize the following results from multiple agents into a coherent final result:

{combined_text}

Provide a comprehensive summary that integrates all the work done."""

            messages = [
                {
                    "role": "system",
                    "content": "You are synthesizing results from multiple AI agents.",
                },
                {"role": "user", "content": prompt},
            ]

            final_output = await self.nim_service.generate_response(
                messages=messages, temperature=0.5, max_tokens=2000
            )

            return {
                "output": final_output,
                "metadata": {
                    "agents_involved": len(successful_results),
                    "subtasks_completed": len(successful_results),
                    "individual_results": successful_results,
                    "success": True,
                },
            }

        except Exception as e:
            logger.error(f"Error aggregating results: {e}")
            return {
                "output": "Error aggregating results",
                "metadata": {"error": str(e), "success": False},
            }


# Global instance
orchestrator = MultiAgentOrchestrator()

