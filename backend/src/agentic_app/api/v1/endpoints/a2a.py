"""A2A Protocol API endpoints."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.core.database import get_db
from agentic_app.schemas.a2a import (
    A2AMessage,
    A2AMessageCreate,
    AgentBroadcast,
    AgentConversationResponse,
    AgentDiscoveryRequest,
    AgentDiscoveryResponse,
    AgentHandoffRequest,
    AgentHelpRequest,
    CoordinationTask,
    MessageResponse,
)
from agentic_app.services.a2a_service import a2a_service
from agentic_app.services.orchestrator_service import orchestrator

router = APIRouter()


@router.post("/messages/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_agent_message(
    message: A2AMessageCreate,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Send a message from one agent to another.
    
    - **from_agent_id**: ID of the sending agent
    - **to_agent_id**: ID of the receiving agent (None for broadcast)
    - **message_type**: Type of message (request, response, handoff, etc.)
    - **content**: Message content
    """
    try:
        result = await a2a_service.send_message(db, message)
        return MessageResponse(
            message_id=result.message_id,
            conversation_id=result.conversation_id,
            status="sent",
            timestamp=result.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/agents/{agent_id}/request-help")
async def request_agent_help(
    agent_id: int,
    request: AgentHelpRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Request help from another agent with a specific capability.
    
    Agent will automatically find and contact an agent with the required capability.
    """
    try:
        # Ensure requesting_agent_id matches path parameter
        request.requesting_agent_id = agent_id
        
        target_agent = await a2a_service.request_help(db, request)
        
        if not target_agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agent found with capability: {request.target_capability}"
            )
        
        return {
            "requesting_agent_id": agent_id,
            "target_agent_id": target_agent.id,
            "target_agent_name": target_agent.name,
            "capability": request.target_capability,
            "status": "request_sent"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request help: {str(e)}"
        )


@router.post("/tasks/handoff")
async def handoff_task(
    handoff: AgentHandoffRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Handoff a task from one agent to another.
    
    Transfers task ownership and sends handoff notification with context.
    """
    try:
        success = await a2a_service.handoff_task(db, handoff)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to handoff task"
            )
        
        return {
            "task_id": handoff.task_id,
            "from_agent_id": handoff.from_agent_id,
            "to_agent_id": handoff.to_agent_id,
            "status": "handed_off",
            "reason": handoff.reason
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handoff task: {str(e)}"
        )


@router.post("/broadcast")
async def broadcast_message(
    broadcast: AgentBroadcast,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Broadcast a message to all agents.
    
    Useful for announcements or coordination across all agents.
    """
    try:
        message_id = await a2a_service.broadcast_to_agents(db, broadcast)
        
        return {
            "message_id": message_id,
            "from_agent_id": broadcast.from_agent_id,
            "status": "broadcasted",
            "requires_acknowledgment": broadcast.requires_acknowledgment
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast message: {str(e)}"
        )


@router.get("/agents/{agent_id}/messages", response_model=List[A2AMessage])
async def get_agent_messages(
    agent_id: int,
    unread_only: bool = False,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
) -> List[A2AMessage]:
    """
    Get messages for a specific agent.
    
    - **agent_id**: ID of the agent
    - **unread_only**: Only return unread messages
    - **limit**: Maximum number of messages to return
    """
    try:
        messages = await a2a_service.get_agent_messages(
            db, agent_id, unread_only=unread_only, limit=limit
        )
        return [A2AMessage.model_validate(msg) for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get messages: {str(e)}"
        )


@router.post("/messages/{message_id}/read")
async def mark_message_read(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Mark a message as read."""
    try:
        success = await a2a_service.mark_message_read(db, message_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return {"message_id": str(message_id), "status": "read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark message as read: {str(e)}"
        )


@router.post("/tasks/{task_id}/coordinate")
async def coordinate_multi_agent_task(
    task_id: int,
    coordinator_agent_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Coordinate multiple agents to complete a complex task.
    
    This endpoint:
    1. Decomposes the task into subtasks
    2. Assigns subtasks to appropriate agents based on capabilities
    3. Coordinates execution across agents
    4. Aggregates results into final output
    
    - **task_id**: ID of the task to coordinate
    - **coordinator_agent_id**: Optional ID of coordinator agent
    """
    try:
        result = await orchestrator.coordinate_task(
            db, task_id, coordinator_agent_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to coordinate task: {str(e)}"
        )


@router.post("/agents/discover", response_model=AgentDiscoveryResponse)
async def discover_agents(
    request: AgentDiscoveryRequest,
    db: AsyncSession = Depends(get_db)
) -> AgentDiscoveryResponse:
    """
    Discover agents with specific capabilities.
    
    - **required_capabilities**: List of capabilities needed
    - **exclude_agents**: List of agent IDs to exclude
    - **max_results**: Maximum number of agents to return
    """
    try:
        from agentic_app.services.agent_service import agent_service
        
        discovered_agents = []
        
        # Find agents for each capability
        for capability in request.required_capabilities:
            agents = await a2a_service._find_agents_by_capability(db, capability)
            
            for agent in agents:
                if agent.id not in request.exclude_agents:
                    discovered_agents.append({
                        "id": agent.id,
                        "name": agent.name,
                        "role": agent.role,
                        "status": agent.status,
                        "capabilities": agent.capabilities or [],
                        "capability_match": capability
                    })
        
        # Remove duplicates and limit results
        unique_agents = {a["id"]: a for a in discovered_agents}.values()
        limited_agents = list(unique_agents)[:request.max_results]
        
        return AgentDiscoveryResponse(
            agents=limited_agents,
            count=len(limited_agents)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover agents: {str(e)}"
        )


@router.websocket("/agents/{agent_id}/messages/stream")
async def agent_message_stream(
    websocket: WebSocket,
    agent_id: int
):
    """
    WebSocket endpoint for real-time agent message streaming.
    
    Agents can connect to this endpoint to receive messages in real-time.
    """
    await websocket.accept()
    
    try:
        # Initialize Redis connection if not already done
        if not a2a_service.redis:
            await a2a_service.initialize_redis()
        
        # Subscribe to agent's message channel
        pubsub = a2a_service.redis.pubsub()
        await pubsub.subscribe(f"agent:{agent_id}")
        
        import asyncio
        import json
        
        async def listen_for_messages():
            """Listen for messages from Redis."""
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        await websocket.send_text(message['data'])
                    except Exception as e:
                        logger.error(f"Error sending message via WebSocket: {e}")
                        break
        
        # Start listening
        await listen_for_messages()
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent {agent_id}")
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {e}")
    finally:
        # Clean up subscription
        try:
            await pubsub.unsubscribe(f"agent:{agent_id}")
            await pubsub.close()
        except:
            pass


# Import logger for WebSocket endpoint
import logging
logger = logging.getLogger(__name__)

