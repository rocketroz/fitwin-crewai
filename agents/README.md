# Agents (CrewAI) — local bootstrap

This directory contains a minimal scaffold to run CrewAI agents locally without touching backend dependencies.

Recommended workflow

1. Create a separate venv for agent development (keeps dependencies isolated from backend):

```bash
python3 -m venv .venv-agents
source .venv-agents/bin/activate
pip install crewai python-dotenv
```

2. Populate `agents/.env` with any required env vars (for example `AGENT_MODEL` or OpenAI keys).

3. Run the bootstrap script:

```bash
python agents/crew/bootstrap.py
```

This script is intentionally minimal — replace the example agents, tasks, and model names to match your environment.
