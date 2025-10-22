"""Example test to demonstrate A2A testing patterns.

This file shows common testing patterns for the A2A protocol.
Use this as a reference when writing your own tests.
"""

import pytest
from unittest.mock import patch

from agentic_app.models.agent import Agent
from agentic_app.models.task import Task, TaskPriority, TaskStatus
from agentic_app.schemas.a2a import A2AMessageCreate, MessageType
from agentic_app.services.a2a_service import A2AService
from agentic_app.services.orchestrator_service import orchestrator


# ============================================================================
# EXAMPLE 1: Simple Message Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_send_simple_message(
    a2a_service: A2AService,
    db_session,
    coordinator_agent: Agent,
    research_agent: Agent
):
    """
    Example: Send a simple message between two agents.
    
    This demonstrates:
    - Using fixtures (a2a_service, db_session, agents)
    - Creating a message
    - Verifying the result
    """
    # Create a message
    message = A2AMessageCreate(
        from_agent_id=coordinator_agent.id,
        to_agent_id=research_agent.id,
        message_type=MessageType.REQUEST,
        content="Can you help me research AI trends?",
        requires_response=True
    )
    
    # Send the message
    result = await a2a_service.send_message(db_session, message)
    
    # Verify the message was sent correctly
    assert result.from_agent_id == coordinator_agent.id
    assert result.to_agent_id == research_agent.id
    assert result.content == "Can you help me research AI trends?"
    assert result.message_id is not None
    assert result.conversation_id is not None


# ============================================================================
# EXAMPLE 2: Help Request Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_agent_requests_help(
    a2a_service: A2AService,
    db_session,
    coordinator_agent: Agent,
    research_agent: Agent,
    capability_registry  # Pre-populated capabilities
):
    """
    Example: One agent requests help from another.
    
    This demonstrates:
    - Agent capability matching
    - Help request workflow
    - Verifying the right agent is found
    """
    from agentic_app.schemas.a2a import AgentHelpRequest
    
    # Create help request
    help_request = AgentHelpRequest(
        requesting_agent_id=coordinator_agent.id,
        target_capability="research",
        query="I need help analyzing market data",
        context="Working on market analysis report",
        urgency="high"
    )
    
    # Request help
    target_agent = await a2a_service.request_help(db_session, help_request)
    
    # Verify the right agent was found
    assert target_agent is not None
    assert target_agent.id == research_agent.id
    assert "research" in target_agent.capabilities


# ============================================================================
# EXAMPLE 3: Simple Workflow Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_simple_workflow(
    db_session,
    research_agent: Agent,
    writer_agent: Agent
):
    """
    Example: Test a simple two-step workflow.
    
    This demonstrates:
    - Creating a task
    - Mocking external dependencies (NIM)
    - Coordinating multiple agents
    - Verifying workflow completion
    """
    # Create a task
    task = Task(
        title="Create AI Report",
        description="Research AI trends and write a comprehensive report",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    
    # Mock NIM responses
    mock_subtasks = '''[
        {
            "description": "Research AI market trends",
            "required_capabilities": ["research"],
            "dependencies": [],
            "estimated_complexity": "medium"
        },
        {
            "description": "Write comprehensive report",
            "required_capabilities": ["writing"],
            "dependencies": [0],
            "estimated_complexity": "medium"
        }
    ]'''
    
    with patch.object(
        orchestrator.nim_service,
        'generate_response',
        side_effect=[
            mock_subtasks,  # Task decomposition
            "Final AI market report completed"  # Result aggregation
        ]
    ), patch.object(
        orchestrator.agent_service,
        'reason_about_task',
        side_effect=[
            "Research completed: AI market analysis done",
            "Report written: Comprehensive AI trends document"
        ]
    ):
        # Coordinate the task
        result = await orchestrator.coordinate_task(db_session, task.id)
        
        # Verify the workflow completed
        assert result["status"] == "completed"
        assert result["subtasks_completed"] >= 1
        assert "final_result" in result
        
        # Verify task was updated
        await db_session.refresh(task)
        assert task.status == TaskStatus.COMPLETED


# ============================================================================
# EXAMPLE 4: Task Handoff Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_task_handoff(
    a2a_service: A2AService,
    db_session,
    research_agent: Agent,
    writer_agent: Agent,
    test_task: Task
):
    """
    Example: Hand off a task from one agent to another.
    
    This demonstrates:
    - Task assignment
    - Handoff between agents
    - Verifying ownership transfer
    """
    from agentic_app.schemas.a2a import AgentHandoffRequest
    
    # Initially assign to research agent
    test_task.agent_id = research_agent.id
    await db_session.commit()
    
    # Create handoff request
    handoff = AgentHandoffRequest(
        from_agent_id=research_agent.id,
        to_agent_id=writer_agent.id,
        task_id=test_task.id,
        context="Research is complete, ready for writing phase",
        reason="Requires specialized writing skills",
        capabilities_needed=["writing", "content_creation"]
    )
    
    # Execute handoff
    success = await a2a_service.handoff_task(db_session, handoff)
    
    # Verify handoff succeeded
    assert success is True
    
    # Verify task ownership changed
    await db_session.refresh(test_task)
    assert test_task.agent_id == writer_agent.id


# ============================================================================
# EXAMPLE 5: Using Test Helpers
# ============================================================================

@pytest.mark.asyncio
async def test_example_using_helpers(db_session):
    """
    Example: Use test helper utilities.
    
    This demonstrates:
    - Using TestDataFactory
    - Creating custom test data
    - Using workflow helpers
    """
    from tests.test_utils import TestDataFactory, WorkflowTestHelpers
    
    # Create a custom agent team
    team = await TestDataFactory.create_agent_team(db_session, {
        "DataScientist": ["data_science", "analysis", "python"],
        "MLEngineer": ["machine_learning", "tensorflow", "model_training"]
    })
    
    # Verify agents were created
    assert "DataScientist" in team
    assert "MLEngineer" in team
    
    # Create a task for the team
    task = await TestDataFactory.create_task(
        db_session,
        title="ML Model Training",
        description="Train and deploy ML model",
        priority=TaskPriority.HIGH
    )
    
    # Verify task was created
    assert task.title == "ML Model Training"
    assert task.status == TaskStatus.PENDING


# ============================================================================
# EXAMPLE 6: Error Handling Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_error_handling(
    a2a_service: A2AService,
    db_session,
    research_agent: Agent
):
    """
    Example: Test error handling.
    
    This demonstrates:
    - Testing error cases
    - Verifying proper error handling
    - Using pytest.raises
    """
    from agentic_app.schemas.a2a import AgentHandoffRequest
    
    # Try to handoff a non-existent task
    handoff = AgentHandoffRequest(
        from_agent_id=research_agent.id,
        to_agent_id=999,  # Non-existent agent
        task_id=99999,  # Non-existent task
        context="Invalid handoff",
        reason="Testing error handling",
        capabilities_needed=[]
    )
    
    # Handoff should fail gracefully
    success = await a2a_service.handoff_task(db_session, handoff)
    
    # Verify it returned False instead of raising an exception
    assert success is False


# ============================================================================
# EXAMPLE 7: Conversation Tracking Test
# ============================================================================

@pytest.mark.asyncio
async def test_example_conversation_tracking(
    a2a_service: A2AService,
    db_session,
    test_task: Task,
    coordinator_agent: Agent,
    research_agent: Agent,
    writer_agent: Agent
):
    """
    Example: Track multi-agent conversations.
    
    This demonstrates:
    - Creating conversations
    - Linking messages to conversations
    - Tracking participating agents
    """
    # Create a conversation for the task
    participating_agents = [
        coordinator_agent.id,
        research_agent.id,
        writer_agent.id
    ]
    
    conversation = await a2a_service.create_conversation(
        db_session,
        test_task.id,
        participating_agents
    )
    
    # Verify conversation was created
    assert conversation.task_id == test_task.id
    assert len(conversation.participating_agents) == 3
    assert conversation.status == "active"
    
    # Send messages in the conversation
    message = A2AMessageCreate(
        from_agent_id=coordinator_agent.id,
        to_agent_id=research_agent.id,
        message_type=MessageType.REQUEST,
        content="Please start research",
        conversation_id=conversation.conversation_id
    )
    
    result = await a2a_service.send_message(db_session, message)
    
    # Verify message is linked to conversation
    assert result.conversation_id == conversation.conversation_id


# ============================================================================
# TIPS FOR WRITING YOUR OWN TESTS
# ============================================================================

"""
1. Always use @pytest.mark.asyncio for async tests

2. Use descriptive test names:
   - test_feature_name_expected_behavior
   - test_error_case_what_should_happen

3. Follow Arrange-Act-Assert pattern:
   - Arrange: Set up test data
   - Act: Execute the function being tested
   - Assert: Verify the results

4. Use fixtures from conftest.py:
   - db_session: Database session
   - a2a_service: A2A service
   - coordinator_agent, research_agent, etc.: Pre-created agents
   - test_task: Sample task
   - capability_registry: Agent capabilities

5. Mock external dependencies:
   - NIM service responses
   - Agent reasoning
   - External API calls

6. Test both success and failure cases

7. Keep tests isolated:
   - Each test should be independent
   - Don't rely on test execution order
   - Use fixtures for setup/teardown

8. Run tests frequently during development:
   ./scripts/test_quick.sh "your_test_name"
"""

