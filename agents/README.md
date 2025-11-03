# Agents: local run & secrets

This guide explains how to protect the OpenAI API key, wire it into GitHub Actions, and run the CrewAI agents locally with a
 clean dependency boundary from the FastAPI backend.

If an API key was ever committed inside `agents/.env`, rotate it now in the OpenAI dashboard and follow the steps below.

## 1. Update GitHub secrets (critical)

1. Revoke the old key in the OpenAI dashboard.
2. Generate a new key and copy it.
3. In GitHub → **Settings → Secrets and variables → Actions → New repository secret**.
4. Name it `OPENAI_API_KEY` (exact string) and paste the key.

The CI job `agents-smoke` pulls this secret at runtime. It only runs in GitHub Actions, so the key is never printed locally.

## 2. Remove local copies of the key

Delete any `.env` that still contains the key so it does not leak again:

```bash
rm -f agents/.env
```

If you want to keep non-secret defaults (for example `AGENT_MODEL`), recreate `agents/.env` after the cleanup without the ke
y.

## 3. Run agents locally (recommended workflow)

We keep agent dependencies in a dedicated virtual environment to avoid collisions with backend packages.

```bash
python3 -m venv .venv-agents
source .venv-agents/bin/activate
pip install --upgrade pip
pip install crewai openai python-dotenv
```

After the environment is ready, choose your launcher:

- **Direct bootstrap**

	```bash
	export OPENAI_API_KEY="sk-..."
	export AGENT_MODEL="gpt-4o-mini"  # optional
	python agents/crew/bootstrap.py
	```

- **Helper script (preferred)**

	```bash
	export OPENAI_API_KEY="sk-..."
	export AGENT_MODEL="gpt-4o-mini"  # optional
	./scripts/run_agents_env.sh
	```

	The helper script activates `.venv-agents`, verifies the key, and then runs `agents/crew/bootstrap.py`.

Extend `agents/crew/`, `agents/prompts/`, and `agents/tools/` as needed; the shipped scaffold is deliberately minimal.

## 4. About the GitHub Actions linter warning

Local static analysis may warn that `secrets.OPENAI_API_KEY` is an "invalid context" inside the workflow. The workflow still
 works in Actions—the warning is local only. Either ignore it or let me know if you'd like a small workflow refactor to sile
nce the warning.

## 5. Troubleshooting

- **CI cannot read the key** → confirm the repo secret exists and Actions are enabled.
- **`smoke_import` fails** → ensure the minimal dependencies (`crewai`, `openai`, `python-dotenv`) install in the workflow st
ep.

If you want a short reminder of these steps in the root `README.md`, just say the word and we can add a summary there.
