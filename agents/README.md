# Agents: local run & secrets

This document explains how to run the local agents, how to securely manage the OpenAI API key, and what to do about the small GitHub Actions linter warning you may see in your editor.

## Rotate an exposed API key (critical)

If you previously placed an API key into `agents/.env`, rotate that key immediately in the OpenAI dashboard and follow these steps:

1. Revoke the old key in the OpenAI dashboard.
2. Create a new API key and copy it.

## Add the new key to GitHub Secrets

1. On GitHub: Settings → Secrets and variables → Actions → New repository secret.
2. Name it `OPENAI_API_KEY` (exactly) and paste the new key value.

The CI job `agents-smoke` uses this secret at runtime. The job will only run on GitHub Actions and will not print the secret.

## Remove local copies of the key

Remove any local `.env` file that contains the key so you don't accidentally commit it or leak it again:

```bash
rm -f agents/.env
```

## Run agents locally (recommended)

We use a separate venv for agents to avoid dependency collisions with the backend.

1. Create and activate the agents venv (example):

```bash
# from the repo root
python3 -m venv .venv-agents
source .venv-agents/bin/activate
pip install --upgrade pip
pip install crewai openai python-dotenv
```

2. Put the new key into your shell (do not commit):

```bash
export OPENAI_API_KEY="sk-..."
./scripts/run_agents.sh
```

`scripts/run_agents.sh` will activate `.venv-agents` and run `agents/crew/bootstrap.py`.

## CI & the linter warning

You may see an editor/static-linter warning about `Context access might be invalid: OPENAI_API_KEY` in the workflow file. This is a local static analysis warning — GitHub Actions itself supports the `secrets` context and your workflow runs on GitHub (see Actions → run history). We verified the CI run succeeded in your repository.

If you want to silence the local warning in your editor, there are two options:

- Ignore it: the workflow runs fine on GitHub and the secret is read at runtime.
- Or, if you prefer, I can further restructure the workflow to reduce the warning noise. It doesn't change runtime behavior; it's only to satisfy the linter.

## Troubleshooting

- If CI fails with a permissions error, ensure the `OPENAI_API_KEY` secret exists in the repo Settings and you have Actions permissions enabled for the repository.
- If imports fail in `agents/smoke_import.py` on CI, ensure the minimal packages (crewai, python-dotenv, openai) are installed in the step.

If you want, I'll (A) rework the workflow to try to silence the linter further, or (B) add a short README section into the repo root `README.md` describing these steps. Tell me which and I'll do it next.
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

## Prefer environment variables for secrets (recommended)

To avoid storing secrets in files, set the `OPENAI_API_KEY` environment variable and run the provided helper script:

```bash
export OPENAI_API_KEY="sk-..."
export AGENT_MODEL="gpt-4o-mini"  # optional
./scripts/run_agents_env.sh
```

The helper script will activate `.venv-agents` if present and will fail early if `OPENAI_API_KEY` is not set.
