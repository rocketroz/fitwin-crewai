#!/bin/bash
# Development server startup script

set -e

# Load environment variables
if [ -f backend/.env ]; then
    export $(cat backend/.env | grep -v '^#' | xargs)
fi

# Start the FastAPI server
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

