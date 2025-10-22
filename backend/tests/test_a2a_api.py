"""Integration tests for A2A API endpoints."""

import uuid
from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.main import app
from agentic_app.models.agent import Agent
from agentic_app.models.task import Task


@pytest.mark.asyncio
class TestA2AMessageEndpoints:
    """Test A2A message API endpoints."""

    async def test_send_message(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test sending a message via API."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/messages/send",
                json={
                    "from_agent_id": coordinator_agent.id,
                    "to_agent_id": research_agent.id,
                    "message_type": "request",
                    "content": "Test message",
                    "requires_response": True
                }
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "message_id" in data
        assert "conversation_id" in data
        assert data["status"] == "sent"

    async def test_get_agent_messages(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        test_messages
    ):
        """Test getting messages for an agent."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/a2a/agents/{research_agent.id}/messages"
            )

        assert response.status_code == status.HTTP_200_OK
        messages = response.json()
        assert isinstance(messages, list)

    async def test_get_unread_messages_only(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        test_messages
    ):
        """Test getting only unread messages."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/a2a/agents/{research_agent.id}/messages",
                params={"unread_only": True}
            )

        assert response.status_code == status.HTTP_200_OK

    async def test_mark_message_read(
        self,
        db_session: AsyncSession,
        test_messages
    ):
        """Test marking a message as read."""
        message = test_messages[0]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/a2a/messages/{message.message_id}/read"
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "read"


@pytest.mark.asyncio
class TestA2AHelpEndpoints:
    """Test A2A help request endpoints."""

    async def test_request_help_success(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent,
        capability_registry
    ):
        """Test successful help request."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/a2a/agents/{coordinator_agent.id}/request-help",
                json={
                    "requesting_agent_id": coordinator_agent.id,
                    "target_capability": "research",
                    "query": "Need help with research",
                    "urgency": "high"
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["target_agent_id"] == research_agent.id
        assert data["status"] == "request_sent"

    async def test_request_help_no_capable_agent(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test help request when no capable agent exists."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/a2a/agents/{coordinator_agent.id}/request-help",
                json={
                    "requesting_agent_id": coordinator_agent.id,
                    "target_capability": "nonexistent",
                    "query": "Need impossible help",
                    "urgency": "low"
                }
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestA2AHandoffEndpoints:
    """Test A2A task handoff endpoints."""

    async def test_handoff_task_success(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        test_task: Task
    ):
        """Test successful task handoff."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/tasks/handoff",
                json={
                    "from_agent_id": research_agent.id,
                    "to_agent_id": writer_agent.id,
                    "task_id": test_task.id,
                    "context": "Research complete",
                    "reason": "Needs writing",
                    "capabilities_needed": ["writing"]
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "handed_off"
        assert data["task_id"] == test_task.id

    async def test_handoff_invalid_task(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test handoff with invalid task."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/tasks/handoff",
                json={
                    "from_agent_id": research_agent.id,
                    "to_agent_id": writer_agent.id,
                    "task_id": 99999,
                    "context": "Invalid",
                    "reason": "Test",
                    "capabilities_needed": []
                }
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
class TestA2ABroadcastEndpoints:
    """Test A2A broadcast endpoints."""

    async def test_broadcast_message(
        self,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test broadcasting a message."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/broadcast",
                json={
                    "from_agent_id": coordinator_agent.id,
                    "message": "System announcement",
                    "requires_acknowledgment": True
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "broadcasted"
        assert "message_id" in data


@pytest.mark.asyncio
class TestA2ADiscoveryEndpoints:
    """Test A2A agent discovery endpoints."""

    async def test_discover_agents_by_capability(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        capability_registry
    ):
        """Test discovering agents by capability."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/agents/discover",
                json={
                    "required_capabilities": ["research"],
                    "exclude_agents": [],
                    "max_results": 10
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "agents" in data
        assert data["count"] > 0

    async def test_discover_agents_with_exclusion(
        self,
        db_session: AsyncSession,
        research_agent: Agent,
        capability_registry
    ):
        """Test discovery with agent exclusion."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/a2a/agents/discover",
                json={
                    "required_capabilities": ["research"],
                    "exclude_agents": [research_agent.id],
                    "max_results": 10
                }
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Excluded agent should not be in results
        agent_ids = [a["id"] for a in data["agents"]]
        assert research_agent.id not in agent_ids


@pytest.mark.asyncio
class TestA2ACoordinationEndpoints:
    """Test multi-agent coordination endpoints."""

    async def test_coordinate_task_success(
        self,
        db_session: AsyncSession,
        test_task: Task,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test successful task coordination."""
        # Mock orchestrator methods
        with patch(
            'agentic_app.services.orchestrator_service.orchestrator.coordinate_task',
            return_value={
                "task_id": test_task.id,
                "status": "completed",
                "conversation_id": str(uuid.uuid4()),
                "coordinator": coordinator_agent.name,
                "participating_agents": 2,
                "subtasks_completed": 1,
                "final_result": {"output": "Success"}
            }
        ):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    f"/api/v1/a2a/tasks/{test_task.id}/coordinate",
                    params={"coordinator_agent_id": coordinator_agent.id}
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["task_id"] == test_task.id

    async def test_coordinate_nonexistent_task(
        self,
        db_session: AsyncSession
    ):
        """Test coordination with non-existent task."""
        with patch(
            'agentic_app.services.orchestrator_service.orchestrator.coordinate_task',
            side_effect=ValueError("Task not found")
        ):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/a2a/tasks/99999/coordinate"
                )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestA2AWebSocket:
    """Test A2A WebSocket endpoints."""

    async def test_websocket_connection(
        self,
        research_agent: Agent
    ):
        """Test WebSocket connection for agent messages."""
        # WebSocket testing requires additional setup
        # This is a placeholder for WebSocket tests
        # You would typically use the starlette TestClient for WebSocket testing
        pass

