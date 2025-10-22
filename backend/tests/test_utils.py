"""Test utilities and helper functions."""

import asyncio
from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentRole, AgentStatus
from agentic_app.models.agent_message import AgentCapabilityRegistry
from agentic_app.models.task import Task, TaskPriority, TaskStatus


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    async def create_agent(
        db: AsyncSession,
        name: str = "TestAgent",
        role: AgentRole = AgentRole.SPECIALIST,
        capabilities: List[str] = None,
        status: AgentStatus = AgentStatus.IDLE
    ) -> Agent:
        """Create a test agent."""
        agent = Agent(
            name=name,
            description=f"{name} description",
            role=role,
            status=status,
            capabilities=capabilities or ["general"],
            model_name="test-model",
            communication_endpoint=f"test://{name.lower()}"
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent

    @staticmethod
    async def create_task(
        db: AsyncSession,
        title: str = "Test Task",
        description: str = "Test task description",
        priority: TaskPriority = TaskPriority.MEDIUM,
        agent_id: int = None
    ) -> Task:
        """Create a test task."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            agent_id=agent_id
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def create_capability_registry(
        db: AsyncSession,
        agent_id: int,
        capability: str,
        confidence: float = 0.9
    ) -> AgentCapabilityRegistry:
        """Create a capability registry entry."""
        registry = AgentCapabilityRegistry(
            agent_id=agent_id,
            capability_name=capability,
            confidence_score=confidence,
            usage_count=0,
            success_rate=1.0
        )
        db.add(registry)
        await db.commit()
        await db.refresh(registry)
        return registry

    @staticmethod
    async def create_agent_team(
        db: AsyncSession,
        team_config: Dict[str, List[str]] = None
    ) -> Dict[str, Agent]:
        """
        Create a team of agents with different capabilities.
        
        Args:
            db: Database session
            team_config: Dict mapping agent names to their capabilities
            
        Returns:
            Dict mapping agent names to Agent objects
        """
        if team_config is None:
            team_config = {
                "Coordinator": ["planning", "coordination"],
                "Researcher": ["research", "analysis"],
                "Writer": ["writing", "content_creation"],
                "Reviewer": ["review", "qa"]
            }

        team = {}
        role_map = {
            "Coordinator": AgentRole.COORDINATOR,
            "Researcher": AgentRole.SPECIALIST,
            "Writer": AgentRole.SPECIALIST,
            "Reviewer": AgentRole.REVIEWER
        }

        for name, capabilities in team_config.items():
            role = role_map.get(name, AgentRole.SPECIALIST)
            agent = await TestDataFactory.create_agent(
                db,
                name=name,
                role=role,
                capabilities=capabilities
            )
            team[name] = agent

            # Create capability registry entries
            for cap in capabilities:
                await TestDataFactory.create_capability_registry(
                    db,
                    agent.id,
                    cap,
                    confidence=0.9
                )

        return team


class WorkflowTestHelpers:
    """Helper functions for testing workflows."""

    @staticmethod
    async def wait_for_task_completion(
        db: AsyncSession,
        task_id: int,
        timeout: int = 30,
        check_interval: float = 0.5
    ) -> Task:
        """
        Wait for a task to complete (or fail).
        
        Args:
            db: Database session
            task_id: Task ID to monitor
            timeout: Maximum time to wait in seconds
            check_interval: How often to check status
            
        Returns:
            The completed task
            
        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        elapsed = 0.0
        
        while elapsed < timeout:
            task = await db.get(Task, task_id)
            
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return task
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

    @staticmethod
    def assert_task_completed_successfully(task: Task):
        """Assert that a task completed successfully."""
        assert task.status == TaskStatus.COMPLETED, \
            f"Expected task to be completed, got {task.status}"
        assert task.completed_at is not None, \
            "Task completed but completed_at not set"
        assert task.output_data is not None, \
            "Task completed but has no output data"

    @staticmethod
    def assert_agent_participated(agent: Agent, conversation_agents: List[int]):
        """Assert that an agent participated in a conversation."""
        assert agent.id in conversation_agents, \
            f"Agent {agent.name} (ID: {agent.id}) did not participate in conversation"

    @staticmethod
    def verify_workflow_result(
        result: Dict,
        expected_status: str = "completed",
        min_agents: int = 1,
        min_subtasks: int = 1
    ):
        """Verify a workflow coordination result."""
        assert "status" in result, "Result missing status field"
        assert result["status"] == expected_status, \
            f"Expected status {expected_status}, got {result['status']}"
        
        assert "participating_agents" in result, "Result missing participating_agents"
        assert result["participating_agents"] >= min_agents, \
            f"Expected at least {min_agents} agents, got {result['participating_agents']}"
        
        assert "subtasks_completed" in result, "Result missing subtasks_completed"
        assert result["subtasks_completed"] >= min_subtasks, \
            f"Expected at least {min_subtasks} subtasks, got {result['subtasks_completed']}"
        
        if expected_status == "completed":
            assert "final_result" in result, "Completed task missing final_result"


class MockHelpers:
    """Helper functions for mocking dependencies."""

    @staticmethod
    def mock_nim_decomposition(subtasks: List[Dict]) -> str:
        """Create a mock NIM response for task decomposition."""
        import json
        return json.dumps(subtasks)

    @staticmethod
    def mock_nim_aggregation(summary: str) -> str:
        """Create a mock NIM response for result aggregation."""
        return summary

    @staticmethod
    def create_mock_subtasks(count: int = 3) -> List[Dict]:
        """Create mock subtasks for testing."""
        return [
            {
                "description": f"Subtask {i+1}",
                "required_capabilities": ["general"],
                "dependencies": [i-1] if i > 0 else [],
                "estimated_complexity": "medium"
            }
            for i in range(count)
        ]

    @staticmethod
    def create_parallel_subtasks(count: int = 3) -> List[Dict]:
        """Create parallel subtasks (no dependencies)."""
        return [
            {
                "description": f"Parallel task {i+1}",
                "required_capabilities": ["general"],
                "dependencies": [],
                "estimated_complexity": "low"
            }
            for i in range(count)
        ]


class AssertionHelpers:
    """Custom assertions for A2A testing."""

    @staticmethod
    def assert_message_sent(message, from_agent_id: int, to_agent_id: int):
        """Assert message was sent correctly."""
        assert message.from_agent_id == from_agent_id
        assert message.to_agent_id == to_agent_id
        assert message.message_id is not None
        assert message.created_at is not None

    @staticmethod
    def assert_conversation_active(conversation):
        """Assert conversation is active."""
        assert conversation.status == "active"
        assert conversation.conversation_id is not None
        assert len(conversation.participating_agents) > 0

    @staticmethod
    def assert_capability_match(agent: Agent, required_capability: str):
        """Assert agent has required capability."""
        assert required_capability in agent.capabilities, \
            f"Agent {agent.name} missing capability: {required_capability}"

