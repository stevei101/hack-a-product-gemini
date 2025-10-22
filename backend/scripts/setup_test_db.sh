#!/bin/bash
# Setup test database for A2A Protocol tests

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🗄️  Setting up test database...${NC}"

# Database configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_NAME="agentic_app_test"

# Check if PostgreSQL is running
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running. Please start PostgreSQL first.${NC}"
    echo ""
    echo "On macOS (Homebrew):"
    echo "  brew services start postgresql@14"
    echo ""
    echo "On Linux:"
    echo "  sudo systemctl start postgresql"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL is running${NC}"

# Drop test database if it exists
echo -e "${BLUE}🗑️  Dropping existing test database (if exists)...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 && \
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "DROP DATABASE $DB_NAME;" || true

# Create test database
echo -e "${BLUE}📦 Creating test database...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;"

echo -e "${GREEN}✅ Test database created: $DB_NAME${NC}"

# Export test database URL
export TEST_DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

echo -e "${BLUE}📝 Test database URL:${NC}"
echo "  $TEST_DATABASE_URL"
echo ""
echo -e "${GREEN}✅ Test database setup complete!${NC}"
echo ""
echo "You can now run tests with:"
echo "  ./scripts/run_tests.sh"

