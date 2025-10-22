# A2A Protocol Testing Guide

Complete guide for testing the Agent-to-Agent (A2A) Protocol orchestration system.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Troubleshooting](#troubleshooting)
7. [CI/CD Integration](#cicd-integration)

## 🚀 Quick Start

### Prerequisites

Before running tests, ensure you have:

- **Python 3.10+** installed
- **PostgreSQL** running (for database tests)
- **Redis** running (optional, for real Redis tests)
- Virtual environment activated

### Setup Test Environment

```bash
# 1. Navigate to backend directory
cd backend

# 2. Setup test database
./scripts/setup_test_db.sh

# 3. Install test dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install pytest pytest-asyncio pytest-cov fakeredis httpx

# 4. Run all tests
./scripts/run_tests.sh all
```

## 📁 Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures and configuration
│   ├── test_a2a_service.py         # Unit tests for A2A service
│   ├── test_orchestrator_service.py # Unit tests for orchestrator
│   ├── test_a2a_api.py             # Integration tests for API
│   ├── test_e2e_workflows.py       # End-to-end workflow tests
│   └── test_utils.py               # Test utilities and helpers
├── pytest.ini                      # Pytest configuration
└── scripts/
    ├── run_tests.sh                # Main test runner
    ├── setup_test_db.sh            # Database setup
    └── test_quick.sh               # Quick test script
```

## 🏃 Running Tests

### Run All Tests

```bash
./scripts/run_tests.sh all
```

### Run Specific Test Categories

```bash
# Unit tests only
./scripts/run_tests.sh unit

# Integration tests only
./scripts/run_tests.sh integration

# End-to-end tests only
./scripts/run_tests.sh e2e

# With coverage report
./scripts/run_tests.sh coverage
```

### Run Specific Test File

```bash
pytest tests/test_a2a_service.py -v
```

### Run Specific Test Function

```bash
pytest tests/test_a2a_service.py::TestA2AServiceMessaging::test_send_message -v
```

### Run Tests Matching Pattern

```bash
# Run all tests with "workflow" in the name
./scripts/test_quick.sh workflow

# Run all tests with "handoff" in the name
pytest tests/ -k "handoff" -v
```

### Run with Different Verbosity

```bash
# Verbose
./scripts/run_tests.sh all -v

# Very verbose (shows all output)
./scripts/run_tests.sh all -vv
```

## 📊 Test Categories

### 1. Unit Tests

Test individual components in isolation.

**Files:**
- `test_a2a_service.py` - A2A service methods
- `test_orchestrator_service.py` - Orchestrator logic
- `test_utils.py` - Utility functions

**What they test:**
- Message sending/receiving
- Agent capability discovery
- Task decomposition
- Result aggregation
- Error handling

**Run:**
```bash
pytest tests/test_a2a_service.py tests/test_orchestrator_service.py -v
```

### 2. Integration Tests

Test API endpoints with database interactions.

**Files:**
- `test_a2a_api.py` - A2A API endpoints

**What they test:**
- HTTP endpoints
- Request/response validation
- Database persistence
- Error responses

**Run:**
```bash
pytest tests/test_a2a_api.py -v
```

### 3. End-to-End Tests

Test complete multi-agent workflows.

**Files:**
- `test_e2e_workflows.py` - Complete workflows

**What they test:**
- Full coordination flows
- Multi-agent collaboration
- Parallel/sequential execution
- Error recovery
- Conversation tracking

**Run:**
```bash
pytest tests/test_e2e_workflows.py -v
```

## ✍️ Writing Tests

### Using Fixtures

The test suite provides many useful fixtures in `conftest.py`:

```python
import pytest

@pytest.mark.asyncio
async def test_my_feature(
    db_session,           # Database session
    coordinator_agent,    # Pre-created coordinator agent
    research_agent,       # Pre-created research agent
    test_task,            # Pre-created task
    a2a_service           # A2A service with fake Redis
):
    # Your test code here
    result = await a2a_service.send_message(db_session, message)
    assert result is not None
```

### Available Fixtures

| Fixture | Description |
|---------|-------------|
| `db_session` | Async database session |
| `fake_redis` | Fake Redis instance |
| `a2a_service` | A2A service with fake Redis |
| `coordinator_agent` | Coordinator agent |
| `research_agent` | Research specialist agent |
| `writer_agent` | Writer specialist agent |
| `reviewer_agent` | Reviewer agent |
| `test_task` | Sample task |
| `capability_registry` | Pre-populated capabilities |
| `conversation` | Active conversation |
| `test_messages` | Sample messages |
| `sample_subtasks` | Sample subtask data |

### Example: Testing Message Sending

```python
@pytest.mark.asyncio
async def test_send_message(
    a2a_service,
    db_session,
    coordinator_agent,
    research_agent
):
    """Test sending a message between agents."""
    from agentic_app.schemas.a2a import A2AMessageCreate, MessageType
    
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
    assert result.message_id is not None
```

### Example: Testing Workflow

```python
@pytest.mark.asyncio
async def test_research_workflow(
    db_session,
    research_agent,
    writer_agent
):
    """Test research -> write workflow."""
    from agentic_app.models.task import Task, TaskPriority
    from agentic_app.services.orchestrator_service import orchestrator
    from unittest.mock import patch
    
    # Create task
    task = Task(
        title="AI Report",
        description="Research and write AI report",
        priority=TaskPriority.HIGH
    )
    db_session.add(task)
    await db_session.commit()
    
    # Mock NIM responses
    with patch.object(
        orchestrator.nim_service,
        'generate_response',
        side_effect=["[subtasks JSON]", "Final result"]
    ):
        result = await orchestrator.coordinate_task(db_session, task.id)
        
        assert result["status"] == "completed"
```

### Using Test Helpers

```python
from tests.test_utils import TestDataFactory, WorkflowTestHelpers

@pytest.mark.asyncio
async def test_custom_workflow(db_session):
    """Test with custom test data."""
    # Create custom agent team
    team = await TestDataFactory.create_agent_team(db_session, {
        "Coordinator": ["planning"],
        "Analyst": ["analysis", "data_science"]
    })
    
    # Create task
    task = await TestDataFactory.create_task(
        db_session,
        title="Data Analysis",
        priority=TaskPriority.HIGH
    )
    
    # Verify result
    WorkflowTestHelpers.verify_workflow_result(
        result,
        expected_status="completed",
        min_agents=2
    )
```

## 🔧 Troubleshooting

### Database Connection Errors

```bash
# Ensure PostgreSQL is running
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Recreate test database
./scripts/setup_test_db.sh
```

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or use the test scripts which set it automatically
./scripts/run_tests.sh all
```

### Redis Connection Errors

Tests use `fakeredis` by default, so Redis doesn't need to be running. If you want to test with real Redis:

```python
# In your test
@pytest.mark.requires_redis
async def test_with_real_redis():
    # Will be skipped if Redis not available
    pass
```

### Async Test Errors

Ensure tests are marked with `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_async_function()
    assert result is not None
```

### Test Database Not Clean

```bash
# Reset test database
./scripts/setup_test_db.sh

# Or drop and recreate manually
psql -U postgres -c "DROP DATABASE agentic_app_test;"
psql -U postgres -c "CREATE DATABASE agentic_app_test;"
```

## 📈 Coverage Reports

### Generate Coverage Report

```bash
./scripts/run_tests.sh coverage
```

This generates:
- **Terminal report** - Shows missing lines
- **HTML report** - Opens `htmlcov/index.html` in browser

### View HTML Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Goals

- **Overall:** > 80%
- **Critical paths:** > 90%
  - Message sending/receiving
  - Task coordination
  - Error handling

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: A2A Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install pytest pytest-asyncio pytest-cov fakeredis httpx
      
      - name: Setup test database
        run: |
          cd backend
          ./scripts/setup_test_db.sh
        env:
          DB_PASSWORD: postgres
      
      - name: Run tests
        run: |
          cd backend
          ./scripts/run_tests.sh coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/htmlcov/index.html
```

## 🎯 Best Practices

### 1. Test Isolation

Each test should be independent:

```python
# ✅ Good - Uses fixtures that reset between tests
@pytest.mark.asyncio
async def test_feature(db_session, research_agent):
    # Test code
    pass

# ❌ Bad - Shares state between tests
global_agent = None

def test_feature():
    global global_agent
    # Test code
```

### 2. Use Mocking Appropriately

Mock external dependencies, not your own code:

```python
# ✅ Good - Mock external NIM service
with patch.object(orchestrator.nim_service, 'generate_response'):
    result = await orchestrator.coordinate_task(db, task_id)

# ❌ Bad - Mocking your own business logic
with patch.object(orchestrator, 'coordinate_task'):
    # This doesn't test anything!
```

### 3. Test Edge Cases

```python
async def test_handoff_nonexistent_task():
    """Test handoff with invalid task ID."""
    # Test error handling
    
async def test_coordination_with_no_agents():
    """Test coordination when no agents available."""
    # Test fallback behavior
```

### 4. Clear Test Names

```python
# ✅ Good
async def test_send_message_creates_conversation_thread():
    pass

# ❌ Bad
async def test_messages():
    pass
```

### 5. Arrange-Act-Assert Pattern

```python
async def test_feature():
    # Arrange - Set up test data
    agent = await create_agent(db)
    task = await create_task(db)
    
    # Act - Execute the feature
    result = await execute_feature(agent, task)
    
    # Assert - Verify results
    assert result.status == "success"
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [A2A Implementation Guide](./A2A_IMPLEMENTATION_COMPLETE.md)
- [A2A Protocol Spec](./A2A_PROTOCOL_IMPLEMENTATION.md)

## 🆘 Getting Help

If tests are failing:

1. **Check the error message** - Often tells you exactly what's wrong
2. **Run with verbose mode** - `pytest -vv` for detailed output
3. **Run single test** - Isolate the failing test
4. **Check fixtures** - Ensure test data is created correctly
5. **Verify database** - Ensure test database is clean

**Common Issues:**
- Database not created → Run `./scripts/setup_test_db.sh`
- Import errors → Set `PYTHONPATH` or use test scripts
- Async errors → Add `@pytest.mark.asyncio` decorator
- Fixture errors → Check `conftest.py` for fixture definitions

---

**Happy Testing! 🧪✨**

