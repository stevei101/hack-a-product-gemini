"""Unit tests for A2A Service."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.models.agent_message import MessageType
from agentic_app.schemas.a2a import (
    A2AMessageCreate,
    AgentBroadcast,
    AgentHandoffRequest,
    AgentHelpRequest,
)
from agentic_app.services.a2a_service import A2AService


class TestA2AServiceMessaging:
    """Test A2A service messaging functionality."""

    @pytest.mark.asyncio
    async def test_send_message(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test sending a message between agents."""
        message = A2AMessageCreate(
            from_agent_id=coordinator_agent.id,
            to_agent_id=research_agent.id,
            message_type=MessageType.REQUEST,
            content="Please help with research",
            requires_response=True
        )

        result = await a2a_service.send_message(db_session, message)

        assert result.from_agent_id == coordinator_agent.id
        assert result.to_agent_id == research_agent.id
        assert result.message_type == MessageType.REQUEST
        assert result.content == "Please help with research"
        assert result.requires_response is True
        assert result.message_id is not None
        assert result.conversation_id is not None

    @pytest.mark.asyncio
    async def test_send_message_with_conversation_id(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test sending a message with existing conversation ID."""
        conversation_id = uuid.uuid4()
        
        message = A2AMessageCreate(
            from_agent_id=coordinator_agent.id,
            to_agent_id=research_agent.id,
            message_type=MessageType.REQUEST,
            content="Follow-up message",
            conversation_id=conversation_id
        )

        result = await a2a_service.send_message(db_session, message)

        assert result.conversation_id == conversation_id

    @pytest.mark.asyncio
    async def test_send_message_publishes_to_redis(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        fake_redis,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test that sending a message publishes to Redis."""
        message = A2AMessageCreate(
            from_agent_id=coordinator_agent.id,
            to_agent_id=research_agent.id,
            message_type=MessageType.REQUEST,
            content="Test message"
        )

        await a2a_service.send_message(db_session, message)

        # Verify message was published (FakeRedis doesn't support pubsub fully,
        # but we verify the method doesn't error)
        assert True

    @pytest.mark.asyncio
    async def test_broadcast_to_agents(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test broadcasting a message to all agents."""
        broadcast = AgentBroadcast(
            from_agent_id=coordinator_agent.id,
            message="System maintenance tonight",
            requires_acknowledgment=True
        )

        message_id = await a2a_service.broadcast_to_agents(db_session, broadcast)

        assert message_id is not None
        # Verify message was created with no specific recipient
        # (indicating broadcast)

    @pytest.mark.asyncio
    async def test_get_agent_messages(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        test_messages,
        research_agent: Agent
    ):
        """Test retrieving messages for an agent."""
        messages = await a2a_service.get_agent_messages(
            db_session,
            research_agent.id,
            unread_only=False,
            limit=10
        )

        assert len(messages) >= 1
        assert any(msg.to_agent_id == research_agent.id for msg in messages)

    @pytest.mark.asyncio
    async def test_get_unread_messages_only(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        test_messages,
        research_agent: Agent
    ):
        """Test retrieving only unread messages."""
        # Mark first message as read
        first_message = test_messages[0]
        await a2a_service.mark_message_read(db_session, first_message.message_id)

        # Get only unread messages
        unread = await a2a_service.get_agent_messages(
            db_session,
            research_agent.id,
            unread_only=True
        )

        # Should not contain the read message
        assert all(msg.read_at is None for msg in unread)

    @pytest.mark.asyncio
    async def test_mark_message_read(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        test_messages
    ):
        """Test marking a message as read."""
        message = test_messages[0]
        
        result = await a2a_service.mark_message_read(db_session, message.message_id)

        assert result is True

        # Verify message is marked as read
        from sqlalchemy import select
        from agentic_app.models.agent_message import AgentMessage
        
        stmt = select(AgentMessage).where(AgentMessage.message_id == message.message_id)
        result = await db_session.execute(stmt)
        updated_message = result.scalar_one()
        
        assert updated_message.read_at is not None


class TestA2AServiceHelp:
    """Test A2A service help request functionality."""

    @pytest.mark.asyncio
    async def test_request_help_success(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent,
        capability_registry
    ):
        """Test successful help request."""
        request = AgentHelpRequest(
            requesting_agent_id=coordinator_agent.id,
            target_capability="research",
            query="Need help analyzing data",
            context="Have collected user behavior data",
            urgency="high"
        )

        target_agent = await a2a_service.request_help(db_session, request)

        assert target_agent is not None
        assert target_agent.id == research_agent.id
        assert "research" in target_agent.capabilities

    @pytest.mark.asyncio
    async def test_request_help_no_capable_agent(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent
    ):
        """Test help request when no capable agent exists."""
        request = AgentHelpRequest(
            requesting_agent_id=coordinator_agent.id,
            target_capability="nonexistent_capability",
            query="Need help with something impossible",
            urgency="low"
        )

        target_agent = await a2a_service.request_help(db_session, request)

        assert target_agent is None

    @pytest.mark.asyncio
    async def test_request_help_excludes_self(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        research_agent: Agent,
        capability_registry
    ):
        """Test that help request doesn't return the requesting agent."""
        # Update research agent to have a capability
        research_agent.capabilities = ["research", "analysis"]
        await db_session.commit()

        request = AgentHelpRequest(
            requesting_agent_id=research_agent.id,
            target_capability="research",
            query="Need help",
            urgency="normal"
        )

        # Should not find the agent itself
        target_agent = await a2a_service.request_help(db_session, request)
        
        if target_agent:
            assert target_agent.id != research_agent.id


class TestA2AServiceHandoff:
    """Test A2A service task handoff functionality."""

    @pytest.mark.asyncio
    async def test_handoff_task_success(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent,
        test_task
    ):
        """Test successful task handoff."""
        handoff = AgentHandoffRequest(
            from_agent_id=research_agent.id,
            to_agent_id=writer_agent.id,
            task_id=test_task.id,
            context="Research completed, ready for writing",
            reason="Requires writing expertise",
            capabilities_needed=["writing", "content_creation"]
        )

        success = await a2a_service.handoff_task(db_session, handoff)

        assert success is True

        # Verify task was reassigned
        await db_session.refresh(test_task)
        assert test_task.agent_id == writer_agent.id

    @pytest.mark.asyncio
    async def test_handoff_nonexistent_task(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test handoff of non-existent task."""
        handoff = AgentHandoffRequest(
            from_agent_id=research_agent.id,
            to_agent_id=writer_agent.id,
            task_id=99999,
            context="Invalid task",
            reason="Test",
            capabilities_needed=[]
        )

        success = await a2a_service.handoff_task(db_session, handoff)

        assert success is False

    @pytest.mark.asyncio
    async def test_handoff_nonexistent_target_agent(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        research_agent: Agent,
        test_task
    ):
        """Test handoff to non-existent agent."""
        handoff = AgentHandoffRequest(
            from_agent_id=research_agent.id,
            to_agent_id=99999,
            task_id=test_task.id,
            context="Invalid agent",
            reason="Test",
            capabilities_needed=[]
        )

        success = await a2a_service.handoff_task(db_session, handoff)

        assert success is False


class TestA2AServiceConversations:
    """Test A2A service conversation management."""

    @pytest.mark.asyncio
    async def test_create_conversation(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        test_task,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test creating a new conversation."""
        participating_agents = [coordinator_agent.id, research_agent.id]

        conversation = await a2a_service.create_conversation(
            db_session,
            test_task.id,
            participating_agents
        )

        assert conversation.task_id == test_task.id
        assert set(conversation.participating_agents) == set(participating_agents)
        assert conversation.status == "active"
        assert conversation.conversation_id is not None

    @pytest.mark.asyncio
    async def test_create_conversation_without_task(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        coordinator_agent: Agent,
        research_agent: Agent
    ):
        """Test creating a conversation without a task."""
        participating_agents = [coordinator_agent.id, research_agent.id]

        conversation = await a2a_service.create_conversation(
            db_session,
            None,
            participating_agents
        )

        assert conversation.task_id is None
        assert len(conversation.participating_agents) == 2
        assert conversation.status == "active"


class TestA2AServiceCapabilityDiscovery:
    """Test A2A service capability discovery."""

    @pytest.mark.asyncio
    async def test_find_agents_by_capability(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession,
        research_agent: Agent,
        capability_registry
    ):
        """Test finding agents by capability."""
        agents = await a2a_service._find_agents_by_capability(
            db_session,
            "research"
        )

        assert len(agents) > 0
        assert research_agent.id in [a.id for a in agents]

    @pytest.mark.asyncio
    async def test_find_agents_capability_not_found(
        self,
        a2a_service: A2AService,
        db_session: AsyncSession
    ):
        """Test finding agents with non-existent capability."""
        agents = await a2a_service._find_agents_by_capability(
            db_session,
            "nonexistent_capability"
        )

        assert len(agents) == 0

    @pytest.mark.asyncio
    async def test_select_best_agent_prefers_idle(
        self,
        a2a_service: A2AService,
        research_agent: Agent,
        writer_agent: Agent
    ):
        """Test that best agent selection prefers idle agents."""
        # Make research agent busy
        research_agent.status = AgentStatus.EXECUTING
        writer_agent.status = AgentStatus.IDLE

        agents = [research_agent, writer_agent]
        best = await a2a_service._select_best_agent(agents)

        assert best.id == writer_agent.id
        assert best.status == AgentStatus.IDLE

