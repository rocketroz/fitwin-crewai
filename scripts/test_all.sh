#!/bin/bash
# Run all tests

set -e

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Running backend tests..."
pytest tests/backend/ -v

echo ""
echo "All tests passed!"

