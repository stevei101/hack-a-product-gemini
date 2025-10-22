"""End-to-end tests for multi-agent workflows."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.models.task import Task, TaskPriority, TaskStatus
from agentic_app.services.a2a_service import a2a_service
from agentic_app.services.orchestrator_service import orchestrator


@pytest.mark.asyncio
class TestSimpleWorkflow:
    """Test simple two-agent workflows."""

    async def test_research_and_write_workflow(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        capability_registry
    ):
        """Test a simple research -> write workflow."""
        # Create task
        task = Task(
            title="AI Market Report",
            description="Research AI market and write report",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Mock NIM responses
        with patch.object(
            orchestrator.nim_service,
            'generate_response',
            side_effect=[
                # Task decomposition response
                '''[
                    {
                        "description": "Research AI market",
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
                ]''',
                # Final aggregation response
                "Comprehensive AI market report completed"
            ]
        ), patch.object(
            orchestrator.agent_service,
            'reason_about_task',
            side_effect=[
                "Market research completed successfully",
                "Report written and finalized"
            ]
        ):
            # Coordinate the task
            result = await orchestrator.coordinate_task(db_session, task.id)

            # Verify results
            assert result["status"] == "completed"
            assert result["subtasks_completed"] >= 1
            assert "final_result" in result

            # Verify task was updated
            await db_session.refresh(task)
            assert task.status == TaskStatus.COMPLETED
            assert task.output_data is not None


@pytest.mark.asyncio
class TestComplexWorkflow:
    """Test complex multi-agent workflows."""

    async def test_full_content_pipeline(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent,
        writer_agent: Agent,
        reviewer_agent: Agent,
        capability_registry
    ):
        """Test full content pipeline: coordinate -> research -> write -> review."""
        # Create complex task
        task = Task(
            title="Product Launch Content",
            description="Create comprehensive product launch content strategy",
            priority=TaskPriority.CRITICAL,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Mock decomposition into 4 subtasks
        mock_subtasks = [
            {
                "description": "Research market and competitors",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "high"
            },
            {
                "description": "Write product positioning",
                "required_capabilities": ["writing"],
                "dependencies": [0],
                "estimated_complexity": "medium"
            },
            {
                "description": "Create content strategy",
                "required_capabilities": ["writing", "planning"],
                "dependencies": [1],
                "estimated_complexity": "high"
            },
            {
                "description": "Review and finalize",
                "required_capabilities": ["review", "qa"],
                "dependencies": [2],
                "estimated_complexity": "low"
            }
        ]

        with patch.object(
            orchestrator,
            '_decompose_task',
            return_value=mock_subtasks
        ), patch.object(
            orchestrator.agent_service,
            'reason_about_task',
            side_effect=[
                "Market research complete",
                "Positioning written",
                "Strategy created",
                "Review passed"
            ]
        ), patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value="Complete product launch content strategy"
        ):
            result = await orchestrator.coordinate_task(
                db_session,
                task.id,
                coordinator_agent.id
            )

            # Verify complete workflow
            assert result["status"] == "completed"
            assert result["subtasks_completed"] == 4
            assert result["coordinator"] == coordinator_agent.name

            # Check all agents participated
            assert result["participating_agents"] >= 4


@pytest.mark.asyncio
class TestParallelExecution:
    """Test parallel subtask execution."""

    async def test_parallel_research_tasks(
        self,
        db_session: AsyncSession,
        research_agent: Agent
    ):
        """Test parallel execution of independent subtasks."""
        # Create a second research agent
        research_agent_2 = Agent(
            name="ResearchAgent2",
            description="Second research agent",
            role="specialist",
            status=AgentStatus.IDLE,
            capabilities=["research", "analysis"],
            model_name="test-model",
            communication_endpoint="test://research2"
        )
        db_session.add(research_agent_2)
        await db_session.commit()

        task = Task(
            title="Multi-topic Research",
            description="Research multiple independent topics",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Two independent subtasks (no dependencies)
        parallel_subtasks = [
            {
                "description": "Research topic A",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "medium"
            },
            {
                "description": "Research topic B",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "medium"
            }
        ]

        with patch.object(
            orchestrator,
            '_decompose_task',
            return_value=parallel_subtasks
        ), patch.object(
            orchestrator.agent_service,
            'reason_about_task',
            side_effect=[
                "Topic A researched",
                "Topic B researched"
            ]
        ), patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value="Combined research results"
        ):
            result = await orchestrator.coordinate_task(db_session, task.id)

            # Both should complete
            assert result["subtasks_completed"] == 2


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in workflows."""

    async def test_workflow_continues_on_partial_failure(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test workflow handles partial failures gracefully."""
        task = Task(
            title="Resilient Task",
            description="Task that should handle failures",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        subtasks = [
            {
                "description": "Subtask 1",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "low"
            },
            {
                "description": "Subtask 2 (will fail)",
                "required_capabilities": ["research"],
                "dependencies": [],
                "estimated_complexity": "low"
            }
        ]

        with patch.object(
            orchestrator,
            '_decompose_task',
            return_value=subtasks
        ), patch.object(
            orchestrator.agent_service,
            'reason_about_task',
            side_effect=[
                "Success",
                Exception("Agent error")
            ]
        ), patch.object(
            orchestrator.nim_service,
            'generate_response',
            return_value="Partial result"
        ):
            result = await orchestrator.coordinate_task(db_session, task.id)

            # Should complete with partial results
            assert "final_result" in result

    async def test_workflow_fails_on_critical_error(
        self,
        db_session: AsyncSession
    ):
        """Test workflow fails completely on critical errors."""
        task = Task(
            title="Failing Task",
            description="Task that will fail",
            priority=TaskPriority.LOW,
            status=TaskStatus.PENDING
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        with patch.object(
            orchestrator,
            '_decompose_task',
            side_effect=Exception("Critical decomposition error")
        ):
            with pytest.raises(Exception):
                await orchestrator.coordinate_task(db_session, task.id)

            # Task should be marked as failed
            await db_session.refresh(task)
            assert task.status == TaskStatus.FAILED


@pytest.mark.asyncio
class TestAgentCommunication:
    """Test agent-to-agent communication in workflows."""

    async def test_agent_help_request_during_task(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        capability_registry,
        a2a_service
    ):
        """Test agent requesting help from another during task execution."""
        from agentic_app.schemas.a2a import AgentHelpRequest

        # Research agent requests help
        help_request = AgentHelpRequest(
            requesting_agent_id=research_agent.id,
            target_capability="writing",
            query="Need help formatting research results",
            urgency="normal"
        )

        target_agent = await a2a_service.request_help(db_session, help_request)

        assert target_agent is not None
        assert target_agent.id == writer_agent.id

        # Verify message was created
        messages = await a2a_service.get_agent_messages(
            db_session,
            writer_agent.id,
            unread_only=True
        )

        assert len(messages) > 0

    async def test_task_handoff_between_agents(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        test_task: Task,
        a2a_service
    ):
        """Test task handoff between agents."""
        from agentic_app.schemas.a2a import AgentHandoffRequest

        # Assign task to research agent first
        test_task.agent_id = research_agent.id
        await db_session.commit()

        # Handoff to writer
        handoff = AgentHandoffRequest(
            from_agent_id=research_agent.id,
            to_agent_id=writer_agent.id,
            task_id=test_task.id,
            context="Research complete, needs writing",
            reason="Specialized writing needed",
            capabilities_needed=["writing"]
        )

        success = await a2a_service.handoff_task(db_session, handoff)

        assert success is True

        # Verify task was reassigned
        await db_session.refresh(test_task)
        assert test_task.agent_id == writer_agent.id


@pytest.mark.asyncio
class TestConversationTracking:
    """Test conversation tracking in multi-agent workflows."""

    async def test_conversation_created_for_coordination(
        self,
        db_session: AsyncSession,
        test_task: Task,
        coordinator_agent: Agent,
        research_agent: Agent,
        a2a_service
    ):
        """Test conversation is created during coordination."""
        # Create conversation
        participating_agents = [coordinator_agent.id, research_agent.id]
        
        conversation = await a2a_service.create_conversation(
            db_session,
            test_task.id,
            participating_agents
        )

        assert conversation.task_id == test_task.id
        assert len(conversation.participating_agents) == 2
        assert conversation.status == "active"

    async def test_messages_linked_to_conversation(
        self,
        db_session: AsyncSession,
        conversation,
        coordinator_agent: Agent,
        research_agent: Agent,
        a2a_service
    ):
        """Test messages are properly linked to conversations."""
        from agentic_app.schemas.a2a import A2AMessageCreate, MessageType

        # Send message in conversation
        message = A2AMessageCreate(
            from_agent_id=coordinator_agent.id,
            to_agent_id=research_agent.id,
            message_type=MessageType.REQUEST,
            content="Start research",
            conversation_id=conversation.conversation_id
        )

        result = await a2a_service.send_message(db_session, message)

        assert result.conversation_id == conversation.conversation_id

