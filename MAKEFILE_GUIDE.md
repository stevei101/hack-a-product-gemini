# Makefile Commands Guide 🚀

Quick reference for all available `make` commands with the updated `uv`-based Python package management.

## 🔧 Backend Setup & Management

### Initial Setup

```bash
# Quick start (creates .env and sets up backend with uv)
make quick-start

# This will:
# 1. Check if uv is installed (install if needed)
# 2. Create virtual environment with uv venv
# 3. Install core dependencies
# 4. Create .env file from template
```

### Installation Commands

```bash
# Install dependencies from requirements.txt
make backend-install

# Install all dependencies (including dev/test)
make backend-install-dev

# Reset environment completely (clean + setup)
make backend-reset
```

### Development

```bash
# Start backend development server
make backend-dev

# Clean backend environment
make backend-clean

# View backend logs
make backend-logs
```

## 🧪 Testing Commands

### Run Tests

```bash
# Run all backend tests
make backend-test

# Quick test (for development)
make backend-test-quick

# Run with coverage report
make backend-test-coverage

# Test API endpoints (requires server running)
make backend-api-test
```

### Test Examples

```bash
# Test a specific function
cd backend && source .venv/bin/activate
./scripts/test_quick.sh "test_send_message"

# Run specific test file
pytest tests/test_a2a_service.py -v

# Run with very verbose output
pytest tests/ -vv
```

## 🐳 Services Management

```bash
# Start PostgreSQL and Redis (using Podman)
make services-start

# Check service status
make services-status

# Stop services
make services-stop

# Remove service containers
make services-clean
```

## 🎨 Frontend Commands

```bash
# Install frontend dependencies
make install

# Start frontend dev server
make dev

# Build frontend for production
make build

# Preview production build
make preview
```

## 🧹 Cleaning Commands

```bash
# Clean frontend build artifacts
make clean

# Clean backend environment
make backend-clean

# Clean everything (frontend + backend)
make clean-all
```

## 🔐 Security Commands

```bash
# Run security scan
make security-scan

# Generate security report
make security-report

# Setup with security scan
make secure-start
```

## 📦 Container Commands (Podman)

```bash
# Build containers
make container-build

# Build and tag for registry
make container-build-registry REGISTRY=ghcr.io/username

# Run containers locally
make container-run

# Stop containers
make container-stop

# Push to registry
make container-push REGISTRY=ghcr.io/username
```

## 🚀 Complete Workflows

### For Testing A2A Protocol

```bash
# 1. Initial setup
make quick-start

# 2. Edit your .env file
nano backend/.env  # Add your NVIDIA API key

# 3. Start services
make services-start

# 4. Install test dependencies
make backend-install-dev

# 5. Run tests
make backend-test-coverage
```

### For Development

```bash
# 1. Full setup
make quick-start

# 2. Configure environment
nano backend/.env

# 3. Start services
make services-start

# 4. Start backend (in one terminal)
make backend-dev

# 5. Start frontend (in another terminal)
make dev
```

### If You Have Issues

```bash
# Reset everything and start fresh
make backend-reset
make quick-start

# Then continue with normal workflow
```

## 📋 Cheat Sheet

| Command | What It Does |
|---------|--------------|
| `make help` | Show all available commands |
| `make quick-start` | Quick setup for testing |
| `make backend-reset` | Clean and rebuild backend |
| `make backend-test` | Run all tests |
| `make backend-test-coverage` | Tests with coverage report |
| `make services-start` | Start PostgreSQL & Redis |
| `make services-status` | Check service status |
| `make backend-dev` | Start backend server |
| `make dev` | Start frontend dev server |
| `make clean-all` | Clean everything |

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'pip'"

**Solution:**
```bash
make backend-reset
```

This was the old issue - now fixed! The Makefile uses `uv` directly instead of trying to use `pip`.

### "uv: command not found"

**Solution:**
```bash
# Install uv manually
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or let the Makefile install it
make backend-setup
```

### Tests Fail with Database Errors

**Solution:**
```bash
# Make sure PostgreSQL is running
make services-start

# Setup test database
cd backend
./scripts/setup_test_db.sh
```

### Virtual Environment Issues

**Solution:**
```bash
# Clean and start fresh
make backend-clean
make backend-setup
```

## 💡 Pro Tips

1. **Always use `make backend-reset` if you have venv issues** - It cleanly removes the old environment and creates a new one with uv.

2. **For quick iteration during testing:**
   ```bash
   make backend-test-quick
   ```

3. **Check what services are running:**
   ```bash
   make services-status
   ```

4. **View all available commands:**
   ```bash
   make help
   ```

5. **Run tests with coverage to see what's tested:**
   ```bash
   make backend-test-coverage
   open backend/htmlcov/index.html
   ```

## 🔄 Migration from pip to uv

If you were using the old setup with `pip`, here's how to migrate:

```bash
# 1. Clean old environment
make backend-clean

# 2. Setup with uv
make backend-setup

# 3. Install all dependencies
make backend-install-dev

# 4. Verify it works
make backend-test
```

That's it! You're now using `uv` for faster, more reliable package management.

## 📚 Additional Resources

- **Testing Guide**: `docs/A2A_TESTING_GUIDE.md`
- **Quick Test Start**: `docs/A2A_QUICK_TEST_START.md`
- **A2A Implementation**: `docs/A2A_IMPLEMENTATION_COMPLETE.md`

---

**For the full command list, run:**
```bash
make help
```

