#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
if [ ! -d ".venv-agents" ]; then
  echo "Missing .venv-agents. Create it with Python 3.11 and install crewai, openai, python-dotenv."
  exit 1
fi
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set in this shell. Export it, then re-run."
  exit 1
fi
source .venv-agents/bin/activate
python agents/crew/bootstrap.py
