#!/bin/bash
# Quick test script for rapid iteration

set -e

cd "$(dirname "$0")/.."

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Run specific test or all tests
if [ -z "$1" ]; then
    echo "Running all tests..."
    pytest tests/ -v --tb=short -x
else
    echo "Running tests matching: $1"
    pytest tests/ -v --tb=short -x -k "$1"
fi

