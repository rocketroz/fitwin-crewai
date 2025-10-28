# Repository Guidelines

## Project Structure & Module Organization
- `backend/app` hosts FastAPI routers, schemas, services, and core utilities; add new endpoints under `routers/` with matching schema updates.
- `agents/` contains CrewAI crews, configs, prompts, and tools; isolate reusable helpers in `agents/tools` and keep prompt engineering assets in `agents/prompts`.
- `frontend/src` currently serves the photo capture stub; group any future UI modules by feature folder.
- `data/supabase` stores migrations and SQL; update these alongside backend schema changes. Mirror code under `tests/backend` or `tests/agents` to match module paths.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate` sets up the shared Python environment.
- `pip install -r requirements-dev.txt` installs pinned FastAPI, pytest, and tooling versions used in CI.
- `bash scripts/dev_server.sh` exports `PYTHONPATH` and runs the backend with reload; use when iterating on API routes.
- `bash scripts/run_agents.sh` boots the CrewAI workflow; pair with `scripts/run_agents_env.sh` to source env vars locally.
- `bash scripts/test_all.sh` executes the consolidated pytest suite; prefer this before pushing.

## Coding Style & Naming Conventions
- Use Python 3.11 features with 4-space indentation, type hints, and descriptive dataclass names; keep module imports absolute from `backend.app` or `agents` roots.
- Favor snake_case for Python, camelCase for frontend JS utilities, and prefix CrewAI task files with the agent role (e.g., `stylist_task.py`).
- Run `pytest --maxfail=1` on touched packages after substantive edits to catch regressions early.

## Testing Guidelines
- Tests live under `tests/backend` and `tests/agents`; mirror production module names (`test_<module>.py`).
- Validate new API contracts with `TestClient` cases and include fixture data under `tests/backend/fixtures` if needed.
- Aim to preserve or raise coverage by extending existing suites rather than adding redundant smoke tests.

## Commit & Pull Request Guidelines
- Follow Conventional Commits seen in history (`chore(agents): update bootstrap`); scope by directory when practical.
- Reference linked issues in the footer (`Refs #123`) and note any config deltas or data migrations.
- PRs should include a short summary, before/after notes, and pasted output from `bash scripts/test_all.sh`; attach screenshots for UI tweaks.

## Security & Configuration Tips
- Copy `.env.example` files into `backend/.env` and `agents/.env`; never commit secrets.
- Set `FITWIN_API_URL` when targeting remote backends and ensure agent keys load via `source scripts/run_agents_env.sh`.
- Keep customer data out of `data/supabase`; stub samples belong under `data/supabase/sql` and should be anonymized.
