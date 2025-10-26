#!/bin/bash
# Run CrewAI agents

set -e

# Load agent environment variables
if [ -f agents/.env ]; then
    export $(cat agents/.env | grep -v '^#' | xargs)
fi

cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Running CrewAI test..."
python3 agents/crew/crew_test.py

