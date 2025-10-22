"""Agent-to-Agent (A2A) communication service."""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional

from redis import asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentic_app.core.config import settings
from agentic_app.models.agent import Agent, AgentStatus
from agentic_app.models.agent_message import (
    AgentCapabilityRegistry,
    AgentConversation,
    AgentMessage,
    MessageType,
)
from agentic_app.models.task import Task
from agentic_app.schemas.a2a import (
    A2AMessageCreate,
    AgentBroadcast,
    AgentHandoffRequest,
    AgentHelpRequest,
)

logger = logging.getLogger(__name__)


class A2AService:
    """Agent-to-Agent communication service."""

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """Initialize A2A service with Redis client."""
        self.redis = redis_client
        self.message_handlers: Dict[str, callable] = {}

    async def initialize_redis(self):
        """Initialize Redis connection if not provided."""
        if not self.redis:
            try:
                redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379")
                self.redis = await aioredis.from_url(
                    redis_url, encoding="utf-8", decode_responses=True
                )
                logger.info("Redis connection established for A2A service")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

    async def send_message(
        self, db: AsyncSession, message: A2AMessageCreate
    ) -> AgentMessage:
        """Send a message from one agent to another."""
        try:
            # Generate message and conversation IDs if not provided
            message_id = uuid.uuid4()
            conversation_id = message.conversation_id or uuid.uuid4()

            # Store message in database
            db_message = AgentMessage(
                message_id=message_id,
                from_agent_id=message.from_agent_id,
                to_agent_id=message.to_agent_id,
                message_type=message.message_type,
                content=message.content,
                message_metadata=message.metadata,
                requires_response=message.requires_response,
                parent_message_id=message.parent_message_id,
                conversation_id=conversation_id,
            )
            db.add(db_message)
            await db.commit()
            await db.refresh(db_message)

            # Publish to Redis for real-time delivery
            if self.redis:
                await self._publish_message_to_redis(db_message)

            logger.info(
                f"Message sent from Agent {message.from_agent_id} to "
                f"{message.to_agent_id or 'ALL'} (type: {message.message_type})"
            )
            return db_message

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await db.rollback()
            raise

    async def _publish_message_to_redis(self, message: AgentMessage):
        """Publish message to Redis pub/sub channel."""
        if not self.redis:
            return

        try:
            # Determine channel (specific agent or broadcast)
            channel = (
                f"agent:{message.to_agent_id}"
                if message.to_agent_id
                else "agents:broadcast"
            )

            # Prepare message payload
            payload = {
                "message_id": str(message.message_id),
                "from_agent_id": message.from_agent_id,
                "to_agent_id": message.to_agent_id,
                "message_type": message.message_type,
                "content": message.content,
                "metadata": message.message_metadata,
                "conversation_id": str(message.conversation_id),
                "created_at": message.created_at.isoformat(),
            }

            await self.redis.publish(channel, json.dumps(payload))
            logger.debug(f"Published message to Redis channel: {channel}")

        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")

    async def request_help(
        self, db: AsyncSession, request: AgentHelpRequest
    ) -> Optional[Agent]:
        """Find and request help from an agent with specific capability."""
        try:
            # Find agents with the needed capability
            capable_agents = await self._find_agents_by_capability(
                db, request.target_capability
            )

            if not capable_agents:
                logger.warning(
                    f"No agents found with capability: {request.target_capability}"
                )
                return None

            # Exclude the requesting agent
            capable_agents = [
                a for a in capable_agents if a.id != request.requesting_agent_id
            ]

            if not capable_agents:
                logger.warning("No other agents available with required capability")
                return None

            # Select best agent (based on load, confidence, etc.)
            target_agent = await self._select_best_agent(capable_agents)

            # Send request message
            message = A2AMessageCreate(
                from_agent_id=request.requesting_agent_id,
                to_agent_id=target_agent.id,
                message_type=MessageType.REQUEST,
                content=request.query,
                metadata={
                    "capability": request.target_capability,
                    "context": request.context,
                    "urgency": request.urgency,
                },
                requires_response=True,
            )

            await self.send_message(db, message)
            
            logger.info(
                f"Help request sent from Agent {request.requesting_agent_id} to "
                f"Agent {target_agent.id} for capability: {request.target_capability}"
            )
            return target_agent

        except Exception as e:
            logger.error(f"Error in request_help: {e}")
            raise

    async def handoff_task(
        self, db: AsyncSession, handoff: AgentHandoffRequest
    ) -> bool:
        """Handoff a task from one agent to another."""
        try:
            # Get task
            task = await db.get(Task, handoff.task_id)
            if not task:
                logger.warning(f"Task {handoff.task_id} not found")
                return False

            # Verify target agent exists
            target_agent = await db.get(Agent, handoff.to_agent_id)
            if not target_agent:
                logger.warning(f"Target agent {handoff.to_agent_id} not found")
                return False

            # Send handoff message
            message = A2AMessageCreate(
                from_agent_id=handoff.from_agent_id,
                to_agent_id=handoff.to_agent_id,
                message_type=MessageType.HANDOFF,
                content=handoff.context,
                metadata={
                    "task_id": handoff.task_id,
                    "reason": handoff.reason,
                    "capabilities_needed": handoff.capabilities_needed,
                },
            )

            await self.send_message(db, message)

            # Update task assignment
            task.agent_id = handoff.to_agent_id
            await db.commit()

            logger.info(
                f"Task {handoff.task_id} handed off from Agent {handoff.from_agent_id} "
                f"to Agent {handoff.to_agent_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error in handoff_task: {e}")
            await db.rollback()
            raise

    async def broadcast_to_agents(
        self, db: AsyncSession, broadcast: AgentBroadcast
    ) -> str:
        """Broadcast a message to all agents."""
        try:
            message = A2AMessageCreate(
                from_agent_id=broadcast.from_agent_id,
                to_agent_id=None,  # None indicates broadcast
                message_type=MessageType.BROADCAST,
                content=broadcast.message,
                metadata=broadcast.metadata or {},  # Schema uses 'metadata', model uses 'message_metadata'
            )

            result = await self.send_message(db, message)
            
            logger.info(
                f"Broadcast message sent from Agent {broadcast.from_agent_id}"
            )
            return str(result.message_id)

        except Exception as e:
            logger.error(f"Error in broadcast_to_agents: {e}")
            raise

    async def get_agent_messages(
        self,
        db: AsyncSession,
        agent_id: int,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[AgentMessage]:
        """Get messages for an agent."""
        try:
            query = select(AgentMessage).where(AgentMessage.to_agent_id == agent_id)

            if unread_only:
                query = query.where(AgentMessage.read_at.is_(None))

            query = query.order_by(AgentMessage.created_at.desc()).limit(limit)

            result = await db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise

    async def mark_message_read(
        self, db: AsyncSession, message_id: uuid.UUID
    ) -> bool:
        """Mark a message as read."""
        try:
            result = await db.execute(
                select(AgentMessage).where(AgentMessage.message_id == message_id)
            )
            message = result.scalar_one_or_none()

            if not message:
                return False

            from datetime import datetime

            message.read_at = datetime.utcnow()
            await db.commit()
            
            logger.debug(f"Message {message_id} marked as read")
            return True

        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            await db.rollback()
            raise

    async def _find_agents_by_capability(
        self, db: AsyncSession, capability: str
    ) -> List[Agent]:
        """Find agents with a specific capability."""
        try:
            # First check capability registry
            result = await db.execute(
                select(Agent)
                .join(AgentCapabilityRegistry)
                .where(
                    AgentCapabilityRegistry.capability_name == capability,
                    Agent.status != AgentStatus.ERROR,
                )
                .order_by(AgentCapabilityRegistry.confidence_score.desc())
            )
            agents = list(result.scalars().all())

            # If no registry entries, fall back to checking agent capabilities array
            if not agents:
                from sqlalchemy import func

                result = await db.execute(
                    select(Agent).where(
                        func.array_position(Agent.capabilities, capability).isnot(None),
                        Agent.status != AgentStatus.ERROR,
                    )
                )
                agents = list(result.scalars().all())

            return agents

        except Exception as e:
            logger.error(f"Error finding agents by capability: {e}")
            return []

    async def _select_best_agent(self, agents: List[Agent]) -> Agent:
        """Select the best agent from a list using load balancing."""
        # Simple implementation: prefer idle agents
        idle_agents = [a for a in agents if a.status == AgentStatus.IDLE]
        if idle_agents:
            return idle_agents[0]

        # If no idle agents, return the first available
        return agents[0]

    async def create_conversation(
        self, db: AsyncSession, task_id: Optional[int], participating_agents: List[int]
    ) -> AgentConversation:
        """Create a new agent conversation thread."""
        try:
            conversation = AgentConversation(
                conversation_id=uuid.uuid4(),
                task_id=task_id,
                participating_agents=participating_agents,
                status="active",
            )

            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)

            logger.info(
                f"Created conversation {conversation.conversation_id} with "
                f"{len(participating_agents)} agents"
            )
            return conversation

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            await db.rollback()
            raise

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")


# Global instance (will be initialized with Redis client)
a2a_service = A2AService()

