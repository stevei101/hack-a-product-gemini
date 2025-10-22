# Quick Start: Testing A2A Orchestration 🚀

Get started testing the Agent-to-Agent Protocol orchestration in 5 minutes!

## Prerequisites Check ✓

```bash
# Check Python version (need 3.10+)
python3 --version

# Check PostgreSQL is running
pg_isready

# Check if you're in the backend directory
pwd  # Should end with /backend
```

## Step 1: Setup (One-time) ⚙️

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install pytest pytest-asyncio pytest-cov fakeredis httpx

# Setup test database
./scripts/setup_test_db.sh
```

## Step 2: Run Your First Test 🧪

```bash
# Run all tests
./scripts/run_tests.sh all

# Or run a quick single test
pytest tests/test_a2a_service.py::TestA2AServiceMessaging::test_send_message -v
```

**Expected Output:**
```
✅ tests/test_a2a_service.py::TestA2AServiceMessaging::test_send_message PASSED
```

## Step 3: Try Different Test Types 🎯

### Unit Tests (Fast)
Test individual components:
```bash
./scripts/run_tests.sh unit
```

### Integration Tests
Test API endpoints:
```bash
./scripts/run_tests.sh integration
```

### End-to-End Tests
Test complete workflows:
```bash
./scripts/run_tests.sh e2e
```

### Coverage Report
See what's tested:
```bash
./scripts/run_tests.sh coverage
open htmlcov/index.html  # View in browser
```

## Step 4: Test Specific Features 🔍

### Test Message Sending

```bash
pytest tests/test_a2a_service.py::TestA2AServiceMessaging -v
```

### Test Task Coordination

```bash
pytest tests/test_orchestrator_service.py::TestEndToEndCoordination -v
```

### Test Multi-Agent Workflows

```bash
pytest tests/test_e2e_workflows.py::TestComplexWorkflow -v
```

## Step 5: Quick Iteration 🔄

When developing, use the quick test script:

```bash
# Test specific function
./scripts/test_quick.sh "test_send_message"

# Test all tests with "workflow" in name
./scripts/test_quick.sh "workflow"

# Test everything
./scripts/test_quick.sh
```

## Common Test Patterns 📋

### Pattern 1: Simple Message Test

```python
@pytest.mark.asyncio
async def test_send_message(a2a_service, db_session, coordinator_agent, research_agent):
    from agentic_app.schemas.a2a import A2AMessageCreate, MessageType
    
    message = A2AMessageCreate(
        from_agent_id=coordinator_agent.id,
        to_agent_id=research_agent.id,
        message_type=MessageType.REQUEST,
        content="Test message"
    )
    
    result = await a2a_service.send_message(db_session, message)
    assert result is not None
```

### Pattern 2: Workflow Test

```python
@pytest.mark.asyncio
async def test_workflow(db_session, test_task, research_agent):
    from agentic_app.services.orchestrator_service import orchestrator
    from unittest.mock import patch
    
    with patch.object(orchestrator.nim_service, 'generate_response'):
        result = await orchestrator.coordinate_task(db_session, test_task.id)
        assert result["status"] == "completed"
```

## Troubleshooting 🔧

### Database Issues

```bash
# Reset test database
./scripts/setup_test_db.sh

# Or manually
psql -U postgres -c "DROP DATABASE agentic_app_test;"
psql -U postgres -c "CREATE DATABASE agentic_app_test;"
```

### Import Errors

```bash
# Set Python path
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or just use the test scripts
./scripts/run_tests.sh all
```

### Tests Hang

If tests hang, check:
1. PostgreSQL is running: `pg_isready`
2. No infinite loops in test mocks
3. Async tests have `@pytest.mark.asyncio` decorator

## What's Being Tested? 📊

### A2A Service (`test_a2a_service.py`)
- ✅ Message sending/receiving
- ✅ Help requests between agents
- ✅ Task handoffs
- ✅ Broadcasting
- ✅ Capability discovery
- ✅ Conversation management

### Orchestrator (`test_orchestrator_service.py`)
- ✅ Task decomposition
- ✅ Agent selection
- ✅ Workflow execution (parallel/sequential)
- ✅ Result aggregation
- ✅ Error handling

### API Endpoints (`test_a2a_api.py`)
- ✅ POST /a2a/messages/send
- ✅ POST /a2a/agents/{id}/request-help
- ✅ POST /a2a/tasks/handoff
- ✅ POST /a2a/broadcast
- ✅ POST /a2a/tasks/{id}/coordinate
- ✅ POST /a2a/agents/discover
- ✅ GET /a2a/agents/{id}/messages

### Workflows (`test_e2e_workflows.py`)
- ✅ Research → Write workflow
- ✅ Full content pipeline (4+ agents)
- ✅ Parallel task execution
- ✅ Error recovery
- ✅ Agent communication
- ✅ Conversation tracking

## Next Steps 🎓

1. **Read the full guide**: `docs/A2A_TESTING_GUIDE.md`
2. **Write your own tests**: Use fixtures from `conftest.py`
3. **Test real workflows**: Create complex multi-agent scenarios
4. **Measure coverage**: Aim for >80% overall coverage

## Quick Reference Card 📇

```bash
# Setup (once)
./scripts/setup_test_db.sh

# Run all tests
./scripts/run_tests.sh all

# Run specific category
./scripts/run_tests.sh [unit|integration|e2e|coverage]

# Quick test by name
./scripts/test_quick.sh "test_name"

# Single test file
pytest tests/test_a2a_service.py -v

# Single test function
pytest tests/test_a2a_service.py::TestA2AServiceMessaging::test_send_message -v

# With coverage
pytest tests/ --cov=src/agentic_app --cov-report=html

# Very verbose
pytest tests/ -vv

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest --lf
```

## Test Data Fixtures Available 🎁

Use these in your tests (from `conftest.py`):

- `db_session` - Clean database session
- `fake_redis` - Fake Redis for testing
- `a2a_service` - A2A service instance
- `coordinator_agent` - Pre-created coordinator
- `research_agent` - Research specialist
- `writer_agent` - Writer specialist
- `reviewer_agent` - Reviewer agent
- `test_task` - Sample task
- `capability_registry` - Agent capabilities
- `conversation` - Active conversation
- `test_messages` - Sample messages

## Success Criteria ✅

Your tests are working if:
- ✅ All tests pass (green checkmarks)
- ✅ Coverage is >80%
- ✅ No database connection errors
- ✅ Tests run in <30 seconds
- ✅ Can run tests individually

## Getting Help 🆘

- **Full guide**: `docs/A2A_TESTING_GUIDE.md`
- **Implementation**: `docs/A2A_IMPLEMENTATION_COMPLETE.md`
- **Protocol spec**: `docs/A2A_PROTOCOL_IMPLEMENTATION.md`

---

**You're ready to test! 🎉**

Start with:
```bash
./scripts/run_tests.sh all -v
```

