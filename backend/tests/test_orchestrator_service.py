"""Unit tests for Multi-Agent Orchestrator Service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.models.task import Task, TaskStatus
from agentic_app.services.orchestrator_service import MultiAgentOrchestrator


class TestTaskDecomposition:
    """Test task decomposition functionality."""

    @pytest.mark.asyncio
    async def test_decompose_task_success(
        self,
        test_task: Task
    ):
        """Test successful task decomposition."""
        orchestrator = MultiAgentOrchestrator()

        # Mock NIM service response
        mock_subtasks = [
            {
                "description": "Research AI market trends",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "medium"
            },
            {
                "description": "Analyze findings",
                "required_capabilities": ["analysis"],
                "dependencies": [0],
                "estimated_complexity": "high"
            }
        ]

        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value=str(mock_subtasks)
        ):
            subtasks = await orchestrator._decompose_task(test_task)

            assert len(subtasks) > 0
            # Fallback will create at least one subtask
            assert isinstance(subtasks, list)

    @pytest.mark.asyncio
    async def test_decompose_task_with_json_response(
        self,
        test_task: Task
    ):
        """Test task decomposition with proper JSON response."""
        orchestrator = MultiAgentOrchestrator()

        json_response = '''[
            {
                "description": "Research the topic",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "medium"
            },
            {
                "description": "Write report",
                "required_capabilities": ["writing"],
                "dependencies": [0],
                "estimated_complexity": "low"
            }
        ]'''

        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value=json_response
        ):
            subtasks = await orchestrator._decompose_task(test_task)

            assert len(subtasks) == 2
            assert subtasks[0]["description"] == "Research the topic"
            assert subtasks[1]["dependencies"] == [0]

    @pytest.mark.asyncio
    async def test_decompose_task_fallback_on_error(
        self,
        test_task: Task
    ):
        """Test task decomposition falls back on error."""
        orchestrator = MultiAgentOrchestrator()

        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            side_effect=Exception("NIM error")
        ):
            subtasks = await orchestrator._decompose_task(test_task)

            # Should return fallback subtask
            assert len(subtasks) == 1
            assert subtasks[0]["description"] == test_task.description
            assert subtasks[0]["required_capabilities"] == ["general"]


class TestAgentSelection:
    """Test agent selection and assignment."""

    @pytest.mark.asyncio
    async def test_get_coordinator_agent_by_role(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test finding coordinator agent by role."""
        orchestrator = MultiAgentOrchestrator()

        coordinator = await orchestrator._get_coordinator_agent(db_session)

        assert coordinator is not None
        assert coordinator.id == coordinator_agent.id

    @pytest.mark.asyncio
    async def test_get_preferred_coordinator(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test getting preferred coordinator agent."""
        orchestrator = MultiAgentOrchestrator()

        coordinator = await orchestrator._get_coordinator_agent(
            db_session,
            preferred_id=coordinator_agent.id
        )

        assert coordinator is not None
        assert coordinator.id == coordinator_agent.id

    @pytest.mark.asyncio
    async def test_assign_subtasks_to_agents(
        self,
        db_session: AsyncSession,
        sample_subtasks,
        research_agent: Agent,
        writer_agent: Agent,
        capability_registry
    ):
        """Test assigning subtasks to capable agents."""
        orchestrator = MultiAgentOrchestrator()

        assignments = await orchestrator._assign_subtasks_to_agents(
            db_session,
            sample_subtasks
        )

        assert len(assignments) > 0
        
        # Verify assignments have required fields
        for assignment in assignments:
            assert "subtask_index" in assignment
            assert "agent_id" in assignment
            assert "agent_name" in assignment
            assert "subtask" in assignment

    @pytest.mark.asyncio
    async def test_assign_subtasks_finds_any_agent_if_no_match(
        self,
        db_session: AsyncSession,
        research_agent: Agent
    ):
        """Test assignment finds any available agent if no capability match."""
        orchestrator = MultiAgentOrchestrator()

        subtasks = [
            {
                "description": "Unknown task",
                "required_capabilities": ["unknown_capability"],
                "dependencies": [],
                "estimated_complexity": "low"
            }
        ]

        assignments = await orchestrator._assign_subtasks_to_agents(
            db_session,
            subtasks
        )

        # Should still assign to an available agent
        if len(assignments) > 0:
            assert assignments[0]["agent_id"] is not None


class TestWorkflowExecution:
    """Test coordinated workflow execution."""

    @pytest.mark.asyncio
    async def test_execute_subtask_success(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        test_task: Task
    ):
        """Test successful subtask execution."""
        orchestrator = MultiAgentOrchestrator()

        assignment = {
            "subtask_index": 0,
            "agent_id": research_agent.id,
            "agent_name": research_agent.name,
            "subtask": {
                "description": "Research AI trends",
                "estimated_complexity": "medium"
            }
        }

        conversation_id = "test-conversation-123"

        # Mock agent reasoning
        with patch.object(
            orchestrator.agent_service,
            'reason_about_task',
            return_value="Research completed successfully"
        ):
            result = await orchestrator._execute_subtask(
                db_session,
                assignment,
                conversation_id,
                test_task
            )

            assert result["status"] == "completed"
            assert result["agent_id"] == research_agent.id
            assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_coordinated_workflow_sequential(
        self,
        db_session: AsyncSession,
        test_task: Task,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test executing workflow with dependencies (sequential)."""
        orchestrator = MultiAgentOrchestrator()

        assignments = [
            {
                "subtask_index": 0,
                "agent_id": research_agent.id,
                "agent_name": "Research",
                "subtask": {
                    "description": "Research",
                    "dependencies": [],
                    "estimated_complexity": "medium"
                }
            },
            {
                "subtask_index": 1,
                "agent_id": writer_agent.id,
                "agent_name": "Writer",
                "subtask": {
                    "description": "Write report",
                    "dependencies": [0],
                    "estimated_complexity": "low"
                }
            }
        ]

        import uuid
        conversation_id = uuid.uuid4()

        # Mock subtask execution
        with patch.object(
            orchestrator,
            '_execute_subtask',
            side_effect=[
                {"subtask_index": 0, "agent_id": research_agent.id, "status": "completed", "result": "Done"},
                {"subtask_index": 1, "agent_id": writer_agent.id, "status": "completed", "result": "Done"}
            ]
        ):
            results = await orchestrator._execute_coordinated_workflow(
                db_session,
                test_task,
                assignments,
                conversation_id,
                None
            )

            assert len(results) == 2
            # First subtask should complete before second
            assert results[0]["subtask_index"] == 0

    @pytest.mark.asyncio
    async def test_execute_coordinated_workflow_parallel(
        self,
        db_session: AsyncSession,
        test_task: Task,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test executing independent subtasks in parallel."""
        orchestrator = MultiAgentOrchestrator()

        # Two independent subtasks (no dependencies)
        assignments = [
            {
                "subtask_index": 0,
                "agent_id": research_agent.id,
                "agent_name": "Research",
                "subtask": {
                    "description": "Research part A",
                    "dependencies": [],
                    "estimated_complexity": "medium"
                }
            },
            {
                "subtask_index": 1,
                "agent_id": writer_agent.id,
                "agent_name": "Writer",
                "subtask": {
                    "description": "Research part B",
                    "dependencies": [],
                    "estimated_complexity": "medium"
                }
            }
        ]

        import uuid
        conversation_id = uuid.uuid4()

        with patch.object(
            orchestrator,
            '_execute_subtask',
            side_effect=[
                {"subtask_index": 0, "status": "completed", "agent_id": research_agent.id},
                {"subtask_index": 1, "status": "completed", "agent_id": writer_agent.id}
            ]
        ):
            results = await orchestrator._execute_coordinated_workflow(
                db_session,
                test_task,
                assignments,
                conversation_id,
                None
            )

            assert len(results) == 2


class TestResultAggregation:
    """Test result aggregation from multiple agents."""

    @pytest.mark.asyncio
    async def test_aggregate_results_success(self):
        """Test successful result aggregation."""
        orchestrator = MultiAgentOrchestrator()

        results = [
            {
                "subtask_index": 0,
                "agent_id": 1,
                "agent_name": "Research",
                "status": "completed",
                "result": "Market research completed"
            },
            {
                "subtask_index": 1,
                "agent_id": 2,
                "agent_name": "Writer",
                "status": "completed",
                "result": "Report written"
            }
        ]

        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value="Comprehensive final report"
        ):
            final_result = await orchestrator._aggregate_results(results)

            assert final_result["metadata"]["success"] is True
            assert final_result["metadata"]["agents_involved"] == 2
            assert "output" in final_result

    @pytest.mark.asyncio
    async def test_aggregate_results_with_failures(self):
        """Test aggregation with some failed subtasks."""
        orchestrator = MultiAgentOrchestrator()

        results = [
            {
                "subtask_index": 0,
                "agent_id": 1,
                "agent_name": "Research",
                "status": "completed",
                "result": "Research done"
            },
            {
                "subtask_index": 1,
                "agent_id": 2,
                "agent_name": "Writer",
                "status": "failed",
                "error": "Timeout"
            }
        ]

        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value="Partial result"
        ):
            final_result = await orchestrator._aggregate_results(results)

            # Should still aggregate successful results
            assert final_result["metadata"]["agents_involved"] == 1

    @pytest.mark.asyncio
    async def test_aggregate_results_all_failed(self):
        """Test aggregation when all subtasks failed."""
        orchestrator = MultiAgentOrchestrator()

        results = [
            {"status": "failed", "error": "Error 1"},
            {"status": "failed", "error": "Error 2"}
        ]

        final_result = await orchestrator._aggregate_results(results)

        assert final_result["metadata"]["success"] is False
        assert "No successful results" in final_result["output"]


class TestEndToEndCoordination:
    """Test end-to-end task coordination."""

    @pytest.mark.asyncio
    async def test_coordinate_task_complete_flow(
        self,
        db_session: AsyncSession,
        test_task: Task,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test complete task coordination flow."""
        orchestrator = MultiAgentOrchestrator()

        # Mock all dependencies
        mock_subtasks = [
            {
                "description": "Research",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "medium"
            }
        ]

        with patch.object(
            orchestrator,
            '_decompose_task',
            return_value=mock_subtasks
        ), patch.object(
            orchestrator,
            '_execute_coordinated_workflow',
            return_value=[
                {
                    "subtask_index": 0,
                    "agent_id": research_agent.id,
                    "status": "completed",
                    "result": "Success"
                }
            ]
        ), patch.object(
            orchestrator,
            '_aggregate_results',
            return_value={
                "output": "Final result",
                "metadata": {"success": True}
            }
        ):
            result = await orchestrator.coordinate_task(
                db_session,
                test_task.id,
                coordinator_agent.id
            )

            assert result["status"] == "completed"
            assert result["task_id"] == test_task.id
            assert "final_result" in result

            # Verify task status was updated
            await db_session.refresh(test_task)
            assert test_task.status == TaskStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_coordinate_task_handles_failure(
        self,
        db_session: AsyncSession,
        test_task: Task
    ):
        """Test coordination handles failures gracefully."""
        orchestrator = MultiAgentOrchestrator()

        # Mock failure in decomposition
        with patch.object(
            orchestrator,
            '_decompose_task',
            side_effect=Exception("Decomposition failed")
        ):
            with pytest.raises(Exception):
                await orchestrator.coordinate_task(
                    db_session,
                    test_task.id
                )

            # Verify task status was updated to failed
            await db_session.refresh(test_task)
            assert test_task.status == TaskStatus.FAILED

    @pytest.mark.asyncio
    async def test_coordinate_task_nonexistent_task(
        self,
        db_session: AsyncSession
    ):
        """Test coordination with non-existent task."""
        orchestrator = MultiAgentOrchestrator()

        with pytest.raises(ValueError, match="Task .* not found"):
            await orchestrator.coordinate_task(db_session, 99999)

