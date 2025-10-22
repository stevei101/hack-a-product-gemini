#!/bin/bash
# Run A2A Protocol tests

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  A2A Protocol Test Suite                  ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"

# Change to backend directory
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt
pip install -q pytest pytest-asyncio pytest-cov fakeredis httpx

# Export test environment variables
echo -e "${BLUE}⚙️  Setting up test environment...${NC}"
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_app_test"
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Parse command line arguments
TEST_TYPE="${1:-all}"
VERBOSE="${2:-}"

run_all_tests() {
    echo -e "${GREEN}🧪 Running all tests...${NC}"
    pytest tests/ $VERBOSE
}

run_unit_tests() {
    echo -e "${GREEN}🧪 Running unit tests...${NC}"
    pytest tests/test_a2a_service.py tests/test_orchestrator_service.py tests/test_utils.py $VERBOSE
}

run_integration_tests() {
    echo -e "${GREEN}🧪 Running integration tests...${NC}"
    pytest tests/test_a2a_api.py $VERBOSE
}

run_e2e_tests() {
    echo -e "${GREEN}🧪 Running end-to-end tests...${NC}"
    pytest tests/test_e2e_workflows.py $VERBOSE
}

run_coverage() {
    echo -e "${GREEN}📊 Running tests with coverage...${NC}"
    pytest tests/ --cov=src/agentic_app --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
}

# Execute based on argument
case "$TEST_TYPE" in
    all)
        run_all_tests
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    e2e)
        run_e2e_tests
        ;;
    coverage)
        run_coverage
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 {all|unit|integration|e2e|coverage} [-v|-vv]${NC}"
        echo ""
        echo "Test types:"
        echo "  all         - Run all tests"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run API integration tests"
        echo "  e2e         - Run end-to-end workflow tests"
        echo "  coverage    - Run all tests with coverage report"
        echo ""
        echo "Verbosity:"
        echo "  -v          - Verbose output"
        echo "  -vv         - Very verbose output"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
else
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi

