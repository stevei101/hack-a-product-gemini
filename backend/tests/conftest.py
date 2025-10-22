"""Pytest configuration and shared fixtures for A2A testing."""

import asyncio
import os
import uuid
from datetime import datetime
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fakeredis import FakeAsyncRedis
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from agentic_app.core.config import settings
from agentic_app.core.database import Base
from agentic_app.models.agent import Agent, AgentRole, AgentStatus
from agentic_app.models.agent_message import (
    AgentCapabilityRegistry,
    AgentConversation,
    AgentMessage,
)
from agentic_app.models.task import Task, TaskPriority, TaskStatus
from agentic_app.services.a2a_service import A2AService


# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_app_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator[FakeAsyncRedis, None]:
    """Create a fake Redis instance for testing."""
    redis = FakeAsyncRedis(decode_responses=True)
    yield redis
    await redis.flushall()
    await redis.close()


@pytest_asyncio.fixture
async def a2a_service(fake_redis) -> A2AService:
    """Create an A2A service instance with fake Redis."""
    service = A2AService(redis_client=fake_redis)
    return service


# Test data fixtures
@pytest_asyncio.fixture
async def coordinator_agent(db_session: AsyncSession) -> Agent:
    """Create a coordinator agent for testing."""
    agent = Agent(
        name="TestCoordinator",
        description="Test coordinator agent",
        role=AgentRole.COORDINATOR,
        status=AgentStatus.IDLE,
        capabilities=["planning", "coordination", "delegation"],
        model_name="test-model",
        communication_endpoint="test://coordinator"
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def research_agent(db_session: AsyncSession) -> Agent:
    """Create a research specialist agent."""
    agent = Agent(
        name="ResearchAgent",
        description="Research specialist",
        role=AgentRole.SPECIALIST,
        status=AgentStatus.IDLE,
        capabilities=["research", "data_gathering", "analysis"],
        model_name="test-model",
        communication_endpoint="test://research"
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def writer_agent(db_session: AsyncSession) -> Agent:
    """Create a writer specialist agent."""
    agent = Agent(
        name="WriterAgent",
        description="Content creation specialist",
        role=AgentRole.SPECIALIST,
        status=AgentStatus.IDLE,
        capabilities=["writing", "content_creation", "editing"],
        model_name="test-model",
        communication_endpoint="test://writer"
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def reviewer_agent(db_session: AsyncSession) -> Agent:
    """Create a reviewer agent."""
    agent = Agent(
        name="ReviewerAgent",
        description="Quality assurance reviewer",
        role=AgentRole.REVIEWER,
        status=AgentStatus.IDLE,
        capabilities=["review", "qa", "quality_control"],
        model_name="test-model",
        communication_endpoint="test://reviewer"
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession, research_agent: Agent) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Market Analysis",
        description="Research AI market and create comprehensive report",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING,
        agent_id=research_agent.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def capability_registry(
    db_session: AsyncSession,
    research_agent: Agent,
    writer_agent: Agent
) -> list[AgentCapabilityRegistry]:
    """Create capability registry entries."""
    capabilities = [
        AgentCapabilityRegistry(
            agent_id=research_agent.id,
            capability_name="research",
            confidence_score=0.95,
            usage_count=10,
            success_rate=0.92
        ),
        AgentCapabilityRegistry(
            agent_id=writer_agent.id,
            capability_name="writing",
            confidence_score=0.90,
            usage_count=8,
            success_rate=0.88
        )
    ]
    
    for cap in capabilities:
        db_session.add(cap)
    
    await db_session.commit()
    
    for cap in capabilities:
        await db_session.refresh(cap)
    
    return capabilities


@pytest_asyncio.fixture
async def conversation(
    db_session: AsyncSession,
    test_task: Task,
    coordinator_agent: Agent,
    research_agent: Agent
) -> AgentConversation:
    """Create a test conversation."""
    conversation = AgentConversation(
        conversation_id=uuid.uuid4(),
        task_id=test_task.id,
        participating_agents=[coordinator_agent.id, research_agent.id],
        status="active"
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)
    return conversation


@pytest_asyncio.fixture
async def test_messages(
    db_session: AsyncSession,
    conversation: AgentConversation,
    coordinator_agent: Agent,
    research_agent: Agent
) -> list[AgentMessage]:
    """Create test messages."""
    messages = [
        AgentMessage(
            message_id=uuid.uuid4(),
            from_agent_id=coordinator_agent.id,
            to_agent_id=research_agent.id,
            message_type="request",
            content="Please research the AI market",
            conversation_id=conversation.conversation_id,
            requires_response=True
        ),
        AgentMessage(
            message_id=uuid.uuid4(),
            from_agent_id=research_agent.id,
            to_agent_id=coordinator_agent.id,
            message_type="response",
            content="Research completed successfully",
            conversation_id=conversation.conversation_id,
            requires_response=False
        )
    ]
    
    for msg in messages:
        db_session.add(msg)
    
    await db_session.commit()
    
    for msg in messages:
        await db_session.refresh(msg)
    
    return messages


# Helper functions
@pytest.fixture
def sample_subtasks():
    """Sample subtasks for testing task decomposition."""
    return [
        {
            "description": "Research AI market trends",
            "required_capabilities": ["research", "data_gathering"],
            "dependencies": [],
            "estimated_complexity": "medium"
        },
        {
            "description": "Analyze research findings",
            "required_capabilities": ["analysis"],
            "dependencies": [0],
            "estimated_complexity": "high"
        },
        {
            "description": "Write comprehensive report",
            "required_capabilities": ["writing", "content_creation"],
            "dependencies": [1],
            "estimated_complexity": "medium"
        },
        {
            "description": "Review and finalize report",
            "required_capabilities": ["review", "qa"],
            "dependencies": [2],
            "estimated_complexity": "low"
        }
    ]

