# Test Database Setup Guide 🗄️

Quick guide to setting up the test database for A2A Protocol tests.

## Prerequisites

- PostgreSQL installed and running
- Backend environment set up (`make backend-setup`)

## Quick Setup (3 steps)

### 1. Start PostgreSQL

```bash
# Option 1: Using Podman (recommended for this project)
make services-start

# Option 2: Using Homebrew (macOS)
brew services start postgresql@14

# Option 3: Using system service (Linux)
sudo systemctl start postgresql

# Verify it's running
pg_isready
```

**Expected output:** `accepting connections` or `/tmp:5432 - accepting connections`

### 2. Create Test Database

```bash
# Run the setup script
cd backend
./scripts/setup_test_db.sh
```

**Expected output:**
```
✅ PostgreSQL is running
📦 Creating test database...
✅ Test database created: agentic_app_test
```

### 3. Run Tests

```bash
cd ..
make backend-test
```

**Expected output:**
```
✅ Tests passing!
```

## Troubleshooting

### ❌ "pg_isready: command not found"

**Problem:** PostgreSQL not installed or not in PATH

**Solution:**
```bash
# macOS
brew install postgresql@14

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib
```

### ❌ "could not connect to server"

**Problem:** PostgreSQL not running

**Solution:**
```bash
# Check status
pg_isready

# Start PostgreSQL
make services-start
# OR
brew services start postgresql@14
```

### ❌ "password authentication failed"

**Problem:** Wrong password in test configuration

**Solution:**

The test database uses these defaults:
- Host: `localhost`
- Port: `5432`
- User: `postgres`
- Password: `postgres`
- Database: `agentic_app_test`

Update the script if your PostgreSQL uses different credentials:

```bash
# Edit the setup script
nano backend/scripts/setup_test_db.sh

# Or set environment variables
export DB_USER=your_user
export DB_PASSWORD=your_password
./scripts/setup_test_db.sh
```

### ❌ "database already exists" error

**Problem:** Test database from previous run exists

**Solution:**
```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE agentic_app_test;"
./scripts/setup_test_db.sh
```

### ❌ Tests collecting but failing with database errors

**Problem:** Test database not created or wrong credentials

**Solution:**
```bash
# 1. Verify PostgreSQL is running
pg_isready

# 2. Recreate test database
cd backend
./scripts/setup_test_db.sh

# 3. Run tests again
cd ..
make backend-test
```

### ❌ "No module named 'agentic_app'"

**Problem:** PYTHONPATH not set (this is handled by Makefile now)

**Solution:**
```bash
# Use the Makefile commands (they set PYTHONPATH)
make backend-test

# If running pytest directly:
cd backend
PYTHONPATH="${PWD}/src:${PYTHONPATH}" pytest tests/ -v
```

### ❌ Import errors for structlog, greenlet, etc.

**Problem:** Missing dependencies

**Solution:**
```bash
cd backend
uv pip install structlog greenlet
```

## Manual Database Setup

If the script doesn't work, you can set up manually:

```bash
# 1. Connect to PostgreSQL
psql -U postgres

# 2. Create test database
CREATE DATABASE agentic_app_test;

# 3. Exit
\q
```

## Verify Setup

```bash
# 1. Check database exists
psql -U postgres -l | grep agentic_app_test

# 2. Run a simple test
cd backend
PYTHONPATH="${PWD}/src" pytest tests/test_example.py::test_example_send_simple_message -v
```

## Clean Slate

If you want to start completely fresh:

```bash
# 1. Stop PostgreSQL
make services-stop

# 2. Remove test database
psql -U postgres -c "DROP DATABASE IF EXISTS agentic_app_test;"

# 3. Start PostgreSQL
make services-start

# 4. Setup test database
cd backend
./scripts/setup_test_db.sh

# 5. Run tests
cd ..
make backend-test
```

## Using Different Database Configuration

If you want to use a different database:

```bash
# Set environment variable before running tests
export TEST_DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/your_test_db"
make backend-test
```

Or edit `backend/tests/conftest.py`:

```python
TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/your_test_db"
```

## Docker/Podman PostgreSQL

If using the project's Podman setup:

```bash
# Start PostgreSQL in container
make services-start

# The service starts with:
# - Port: 5432
# - User: postgres
# - Password: postgres
# - Database: agentic_app (for dev), agentic_app_test (for tests)

# Check it's running
make services-status

# Setup test database
cd backend
./scripts/setup_test_db.sh
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make services-start` | Start PostgreSQL |
| `make services-status` | Check if running |
| `make services-stop` | Stop PostgreSQL |
| `pg_isready` | Verify connection |
| `./scripts/setup_test_db.sh` | Create test DB |
| `make backend-test` | Run all tests |
| `make backend-test-quick` | Quick test iteration |

## Success Checklist

- [ ] PostgreSQL is running (`pg_isready`)
- [ ] Test database created (`psql -l | grep agentic_app_test`)
- [ ] Dependencies installed (`uv pip install structlog greenlet`)
- [ ] Tests collect successfully (50 items)
- [ ] Tests run (even if some fail initially)

## Next Steps

Once your test database is set up:

1. **Run all tests:** `make backend-test`
2. **Run with coverage:** `make backend-test-coverage`
3. **Quick iteration:** `make backend-test-quick`
4. **View coverage:** `open backend/htmlcov/index.html`

---

**Need help?** Check:
- `docs/A2A_TESTING_GUIDE.md` - Full testing documentation
- `docs/A2A_QUICK_TEST_START.md` - 5-minute quickstart
- `MAKEFILE_GUIDE.md` - All make commands

