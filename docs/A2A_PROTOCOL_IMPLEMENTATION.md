# Agent-to-Agent (A2A) Protocol Implementation Plan

## Overview

This document outlines the implementation plan for adding Agent-to-Agent (A2A) protocol support to The Product Mindset agentic application, enabling multi-agent coordination and collaboration.

## Current State Analysis

### ✅ What We Have
- Individual agent CRUD operations
- Single-agent task execution
- Agent reasoning capabilities (NVIDIA NIM)
- Agent status management
- Task assignment to single agents

### ❌ What's Missing
- Inter-agent communication protocol
- Agent discovery and registration
- Message routing between agents
- Collaborative task decomposition
- Shared context and memory
- Agent orchestration layer

## A2A Protocol Design

### 1. Protocol Standards

We'll implement support for multiple A2A standards:

**Option A: Custom A2A Protocol (Recommended for MVP)**
- RESTful API for agent communication
- JSON-based message format
- WebSocket support for real-time coordination

**Option B: Industry Standards (Future)**
- [Agent Communication Language (ACL)](https://www.fipa.org/specs/fipa00061/)
- OpenAI Swarm-compatible patterns
- LangGraph multi-agent support

### 2. Core Components

```
┌─────────────────────────────────────────────────────────┐
│              A2A Orchestration Layer                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Agent Discovery Service                          │  │
│  │  - Agent registry                                 │  │
│  │  - Capability matching                            │  │
│  │  - Health checking                                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Message Broker (Redis + WebSocket)               │  │
│  │  - Agent-to-agent messaging                       │  │
│  │  - Pub/Sub for broadcasts                         │  │
│  │  - Message queuing                                │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Coordination Service                             │  │
│  │  - Task decomposition                             │  │
│  │  - Agent selection                                │  │
│  │  - Workflow orchestration                         │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Shared Memory / Context Store                    │  │
│  │  - Vector store (ChromaDB)                        │  │
│  │  - Shared workspace                               │  │
│  │  - Conversation history                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
          ↓              ↓              ↓
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Agent A │ ⟷  │ Agent B │ ⟷  │ Agent C │
    └─────────┘    └─────────┘    └─────────┘
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

#### 1.1 Database Schema Updates

**New Tables:**
```sql
-- Agent-to-Agent Messages
CREATE TABLE agent_messages (
    id SERIAL PRIMARY KEY,
    from_agent_id INT REFERENCES agents(id),
    to_agent_id INT REFERENCES agents(id),
    message_type VARCHAR(50),  -- request, response, broadcast, handoff
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    read_at TIMESTAMP
);

-- Agent Conversations (multi-agent threads)
CREATE TABLE agent_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id UUID UNIQUE,
    task_id INT REFERENCES tasks(id),
    participating_agents INT[],
    status VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Agent Capabilities Registry
CREATE TABLE agent_capabilities_registry (
    id SERIAL PRIMARY KEY,
    agent_id INT REFERENCES agents(id),
    capability_name VARCHAR(100),
    capability_description TEXT,
    confidence_score FLOAT,
    last_updated TIMESTAMP
);
```

#### 1.2 Agent Model Updates

**backend/src/agentic_app/models/agent.py:**
```python
class AgentRole(str, Enum):
    """Agent role in multi-agent system."""
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"

class Agent(Base):
    # ... existing fields ...
    
    # A2A Protocol fields
    role: Mapped[Optional[AgentRole]] = mapped_column(String(20), nullable=True)
    communication_endpoint: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    trusted_agents: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer), nullable=True)
    collaboration_history: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
```

### Phase 2: Message Protocol (Week 2-3)

#### 2.1 Message Schema

**backend/src/agentic_app/schemas/a2a.py:**
```python
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MessageType(str, Enum):
    """A2A message types."""
    REQUEST = "request"           # Agent requests help
    RESPONSE = "response"          # Agent responds to request
    HANDOFF = "handoff"           # Transfer task to another agent
    BROADCAST = "broadcast"        # Announce to all agents
    COORDINATE = "coordinate"      # Coordination message
    DELEGATE = "delegate"          # Delegate subtask

class A2AMessage(BaseModel):
    """Agent-to-Agent message format."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent_id: int
    to_agent_id: Optional[int] = None  # None for broadcast
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False
    parent_message_id: Optional[str] = None
    conversation_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentHandoff(BaseModel):
    """Agent handoff request."""
    from_agent_id: int
    to_agent_id: int
    task_id: int
    context: str
    reason: str
    capabilities_needed: List[str]

class AgentRequest(BaseModel):
    """Agent requesting help from another agent."""
    requesting_agent_id: int
    target_capability: str
    query: str
    context: Optional[str] = None
    urgency: str = "normal"  # low, normal, high, critical
```

#### 2.2 A2A Service

**backend/src/agentic_app/services/a2a_service.py:**
```python
import asyncio
import logging
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from agentic_app.models.agent import Agent
from agentic_app.schemas.a2a import A2AMessage, MessageType, AgentHandoff

logger = logging.getLogger(__name__)

class A2AService:
    """Agent-to-Agent communication service."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.message_handlers = {}
        
    async def send_message(
        self,
        db: AsyncSession,
        message: A2AMessage
    ) -> str:
        """Send a message from one agent to another."""
        # Store message in database
        db_message = AgentMessage(
            from_agent_id=message.from_agent_id,
            to_agent_id=message.to_agent_id,
            message_type=message.message_type,
            content=message.content,
            metadata=message.metadata
        )
        db.add(db_message)
        await db.commit()
        
        # Publish to Redis for real-time delivery
        channel = f"agent:{message.to_agent_id}" if message.to_agent_id else "agents:broadcast"
        await self.redis.publish(
            channel,
            message.model_dump_json()
        )
        
        logger.info(f"Message sent from Agent {message.from_agent_id} to {message.to_agent_id or 'ALL'}")
        return message.message_id
    
    async def request_help(
        self,
        db: AsyncSession,
        requesting_agent: Agent,
        capability_needed: str,
        query: str,
        context: Optional[str] = None
    ) -> Optional[Agent]:
        """Find and request help from an agent with specific capability."""
        # Find agents with the needed capability
        capable_agents = await self._find_agents_by_capability(
            db, capability_needed
        )
        
        if not capable_agents:
            logger.warning(f"No agents found with capability: {capability_needed}")
            return None
        
        # Select best agent (based on load, confidence, etc.)
        target_agent = await self._select_best_agent(capable_agents)
        
        # Send request message
        request_message = A2AMessage(
            from_agent_id=requesting_agent.id,
            to_agent_id=target_agent.id,
            message_type=MessageType.REQUEST,
            content=query,
            metadata={
                "capability": capability_needed,
                "context": context,
                "urgency": "normal"
            },
            requires_response=True,
            conversation_id=str(uuid.uuid4())
        )
        
        await self.send_message(db, request_message)
        return target_agent
    
    async def handoff_task(
        self,
        db: AsyncSession,
        handoff: AgentHandoff
    ) -> bool:
        """Handoff a task from one agent to another."""
        # Update task assignment
        task = await db.get(Task, handoff.task_id)
        if not task:
            return False
        
        # Send handoff message
        handoff_message = A2AMessage(
            from_agent_id=handoff.from_agent_id,
            to_agent_id=handoff.to_agent_id,
            message_type=MessageType.HANDOFF,
            content=handoff.context,
            metadata={
                "task_id": handoff.task_id,
                "reason": handoff.reason,
                "capabilities_needed": handoff.capabilities_needed
            },
            conversation_id=str(uuid.uuid4())
        )
        
        await self.send_message(db, handoff_message)
        
        # Update task assignment
        task.agent_id = handoff.to_agent_id
        await db.commit()
        
        logger.info(f"Task {handoff.task_id} handed off from Agent {handoff.from_agent_id} to {handoff.to_agent_id}")
        return True
    
    async def broadcast_to_agents(
        self,
        db: AsyncSession,
        from_agent_id: int,
        message: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """Broadcast a message to all agents."""
        broadcast_message = A2AMessage(
            from_agent_id=from_agent_id,
            to_agent_id=None,
            message_type=MessageType.BROADCAST,
            content=message,
            metadata=metadata or {},
            conversation_id=str(uuid.uuid4())
        )
        
        await self.send_message(db, broadcast_message)
        return broadcast_message.message_id
    
    async def _find_agents_by_capability(
        self,
        db: AsyncSession,
        capability: str
    ) -> List[Agent]:
        """Find agents with a specific capability."""
        result = await db.execute(
            select(Agent).where(
                Agent.capabilities.contains([capability]),
                Agent.status != AgentStatus.ERROR
            )
        )
        return result.scalars().all()
    
    async def _select_best_agent(
        self,
        agents: List[Agent]
    ) -> Agent:
        """Select the best agent from a list (load balancing logic)."""
        # Simple implementation: choose idle agent or least recently active
        idle_agents = [a for a in agents if a.status == AgentStatus.IDLE]
        if idle_agents:
            return idle_agents[0]
        return agents[0]

# Global instance
a2a_service = None  # Initialize with Redis client
```

### Phase 3: Orchestration Layer (Week 3-4)

#### 3.1 Multi-Agent Coordinator

**backend/src/agentic_app/services/orchestrator_service.py:**
```python
class MultiAgentOrchestrator:
    """Orchestrates multi-agent collaboration."""
    
    async def coordinate_task(
        self,
        db: AsyncSession,
        task_id: int
    ) -> Dict[str, Any]:
        """Coordinate multiple agents to complete a complex task."""
        task = await db.get(Task, task_id)
        
        # 1. Decompose task into subtasks
        subtasks = await self._decompose_task(task)
        
        # 2. Match subtasks to agent capabilities
        assignments = await self._assign_subtasks_to_agents(db, subtasks)
        
        # 3. Create conversation thread for coordination
        conversation_id = await self._create_conversation(db, task_id, assignments)
        
        # 4. Execute subtasks in parallel or sequence
        results = await self._execute_coordinated_workflow(
            db, assignments, conversation_id
        )
        
        # 5. Aggregate results
        final_result = await self._aggregate_results(results)
        
        return final_result
    
    async def _decompose_task(self, task: Task) -> List[Dict]:
        """Decompose complex task using NIM reasoning."""
        # Use NVIDIA NIM to break down task
        prompt = f"""Decompose this task into subtasks:
        
        Task: {task.description}
        
        Return a JSON array of subtasks with:
        - description
        - required_capabilities
        - dependencies (indices of prerequisite subtasks)
        - estimated_complexity
        """
        
        response = await nim_service.generate_response([
            {"role": "system", "content": "You are a task decomposition expert."},
            {"role": "user", "content": prompt}
        ])
        
        return json.loads(response)
```

### Phase 4: API Endpoints (Week 4)

**backend/src/agentic_app/api/v1/endpoints/a2a.py:**
```python
from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/messages/send")
async def send_agent_message(
    message: A2AMessage,
    db: AsyncSession = Depends(get_db)
):
    """Send a message between agents."""
    message_id = await a2a_service.send_message(db, message)
    return {"message_id": message_id, "status": "sent"}

@router.post("/agents/{agent_id}/request-help")
async def request_agent_help(
    agent_id: int,
    capability: str,
    query: str,
    context: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Request help from another agent."""
    agent = await agent_service.get_agent(db, agent_id)
    target_agent = await a2a_service.request_help(
        db, agent, capability, query, context
    )
    return {"target_agent_id": target_agent.id if target_agent else None}

@router.post("/tasks/{task_id}/coordinate")
async def coordinate_multi_agent_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Coordinate multiple agents for a complex task."""
    result = await orchestrator.coordinate_task(db, task_id)
    return result

@router.websocket("/agents/{agent_id}/messages")
async def agent_message_stream(
    websocket: WebSocket,
    agent_id: int
):
    """WebSocket endpoint for real-time agent messages."""
    await websocket.accept()
    
    # Subscribe to agent's message channel
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"agent:{agent_id}")
    
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await websocket.send_text(message['data'])
    except WebSocketDisconnect:
        await pubsub.unsubscribe(f"agent:{agent_id}")
```

## Configuration Updates

### Environment Variables

Add to `backend/.env`:
```bash
# A2A Protocol Configuration
A2A_ENABLED=true
A2A_MESSAGE_BROKER=redis
A2A_MAX_AGENTS_PER_TASK=5
A2A_COORDINATION_TIMEOUT=300
A2A_MESSAGE_RETENTION_DAYS=7
```

### Dependencies

Add to `backend/pyproject.toml`:
```toml
dependencies = [
    # ... existing ...
    "redis[asyncio]>=5.0.0",
    "websockets>=12.0",
]
```

## Testing Strategy

1. **Unit Tests**: Test individual A2A components
2. **Integration Tests**: Test multi-agent workflows
3. **Load Tests**: Test with multiple concurrent agents
4. **Simulation Tests**: Test complex coordination scenarios

## Monitoring & Observability

```python
# Add metrics for A2A operations
- agent_messages_sent_total
- agent_messages_received_total
- agent_handoffs_total
- multi_agent_tasks_completed
- agent_coordination_duration_seconds
```

## Security Considerations

1. **Agent Authentication**: Verify agent identity in messages
2. **Message Encryption**: Encrypt sensitive inter-agent messages
3. **Rate Limiting**: Prevent message spam between agents
4. **Access Control**: Define which agents can communicate
5. **Audit Logging**: Log all inter-agent interactions

## Future Enhancements

- **Agent Learning**: Agents learn from successful collaborations
- **Dynamic Teams**: Auto-form agent teams based on task requirements
- **Negotiation Protocol**: Agents negotiate task assignments
- **Conflict Resolution**: Handle conflicting agent responses
- **Agent Reputation**: Track agent reliability and performance

## Success Metrics

- [ ] Agents can discover each other's capabilities
- [ ] Agents can send/receive messages
- [ ] Tasks can be decomposed and assigned to multiple agents
- [ ] Agents can handoff tasks to specialized agents
- [ ] Multi-agent workflows complete successfully
- [ ] Real-time coordination via WebSocket
- [ ] < 100ms message latency between agents
- [ ] Support for 10+ concurrent agent conversations

---

**Next Steps:**
1. Review and approve this implementation plan
2. Set up Redis for message broker
3. Start with Phase 1: Database schema updates
4. Implement A2A message protocol
5. Build orchestration layer
6. Create API endpoints
7. Test with real multi-agent scenarios

