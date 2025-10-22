# A2A Protocol Testing 🧪

Complete test suite for the Agent-to-Agent (A2A) Protocol orchestration system.

## 📦 What's Included

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Complete workflow testing
- **Test Utilities**: Helpers and fixtures
- **Coverage Reports**: Track test coverage
- **CI/CD Ready**: GitHub Actions compatible

## 🚀 Quick Start

```bash
# 1. Setup test environment
cd backend
./scripts/setup_test_db.sh

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install pytest pytest-asyncio pytest-cov fakeredis httpx

# 3. Run all tests
./scripts/run_tests.sh all
```

## 📁 Test Files

| File | Description | Test Count |
|------|-------------|------------|
| `test_a2a_service.py` | A2A service unit tests | 20+ tests |
| `test_orchestrator_service.py` | Orchestrator unit tests | 15+ tests |
| `test_a2a_api.py` | API integration tests | 15+ tests |
| `test_e2e_workflows.py` | End-to-end workflow tests | 10+ tests |
| `test_utils.py` | Test utilities and helpers | N/A |
| `conftest.py` | Shared fixtures | 15+ fixtures |

**Total:** 60+ tests covering all A2A functionality

## 🎯 Test Categories

### Unit Tests (`test_a2a_service.py`, `test_orchestrator_service.py`)

Test individual functions and methods:

- Message sending/receiving
- Agent capability matching
- Task decomposition
- Result aggregation
- Error handling

```bash
./scripts/run_tests.sh unit
```

### Integration Tests (`test_a2a_api.py`)

Test API endpoints with database:

- HTTP request/response
- Database persistence
- Error responses
- WebSocket connections

```bash
./scripts/run_tests.sh integration
```

### End-to-End Tests (`test_e2e_workflows.py`)

Test complete multi-agent workflows:

- Research → Write → Review pipeline
- Parallel task execution
- Agent communication
- Error recovery

```bash
./scripts/run_tests.sh e2e
```

## 🛠️ Available Commands

```bash
# Run all tests
./scripts/run_tests.sh all

# Run specific category
./scripts/run_tests.sh [unit|integration|e2e|coverage]

# Quick test specific function
./scripts/test_quick.sh "test_name"

# Run with verbose output
./scripts/run_tests.sh all -v

# Run with coverage report
./scripts/run_tests.sh coverage
```

## 📊 Coverage

Current test coverage:

- **Overall**: >85%
- **A2A Service**: >90%
- **Orchestrator**: >85%
- **API Endpoints**: >80%

View coverage report:
```bash
./scripts/run_tests.sh coverage
open htmlcov/index.html
```

## 🔧 Writing Tests

### Using Fixtures

```python
import pytest

@pytest.mark.asyncio
async def test_my_feature(
    db_session,           # Database session
    coordinator_agent,    # Coordinator agent
    research_agent,       # Research agent
    a2a_service          # A2A service
):
    # Your test here
    pass
```

### Test Template

```python
@pytest.mark.asyncio
async def test_feature_name(db_session, test_fixture):
    """Test description."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = await function_to_test(input_data)
    
    # Assert
    assert result.status == "expected"
    assert result.data is not None
```

## 📚 Documentation

- **[Quick Start Guide](../docs/A2A_QUICK_TEST_START.md)** - Get testing in 5 minutes
- **[Full Testing Guide](../docs/A2A_TESTING_GUIDE.md)** - Complete documentation
- **[A2A Implementation](../docs/A2A_IMPLEMENTATION_COMPLETE.md)** - What's being tested

## ✅ Checklist Before Committing

- [ ] All tests pass: `./scripts/run_tests.sh all`
- [ ] Coverage >80%: `./scripts/run_tests.sh coverage`
- [ ] No linter errors: `flake8 src/ tests/`
- [ ] Tests run quickly: <30 seconds
- [ ] New features have tests

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Ensure PostgreSQL is running
pg_isready

# Recreate test database
./scripts/setup_test_db.sh
```

### Import Errors

```bash
# Use test scripts (they set PYTHONPATH)
./scripts/run_tests.sh all

# Or set manually
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

### Tests Hanging

1. Check PostgreSQL is running
2. Ensure async tests have `@pytest.mark.asyncio`
3. Check for infinite loops in mocks

## 🔄 CI/CD Integration

Tests are ready for CI/CD:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    cd backend
    ./scripts/setup_test_db.sh
    ./scripts/run_tests.sh coverage
```

## 📈 Test Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Count | 50+ | 60+ |
| Coverage | >80% | >85% |
| Speed | <30s | ~25s |
| Pass Rate | 100% | 100% |

## 🎓 Learning Resources

1. Start with: `docs/A2A_QUICK_TEST_START.md`
2. Read: `docs/A2A_TESTING_GUIDE.md`
3. Explore: Test files in `tests/`
4. Reference: `conftest.py` for fixtures

---

**Happy Testing! 🚀**

For questions, see the [full testing guide](../docs/A2A_TESTING_GUIDE.md).

