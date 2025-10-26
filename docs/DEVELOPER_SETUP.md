# Developer quick setup — FitTwin

This file explains how to reproduce the exact development/test environment used for local verification and CI.
Keep it short — copy/paste the commands below.

## Prerequisites
- macOS / Linux
- Python 3.12 installed and available as `python3`
- git

## Quick (copy-and-run)
```bash
# from repo root
cd ~/fitwin-crewai

# create and activate a project venv
python3 -m venv .venv
source .venv/bin/activate

# install pinned dev/test deps (used by CI)
pip install -r requirements-dev.txt

# run tests (offline, deterministic)
bash scripts/test_all.sh

# start dev server (for manual API checks)
bash scripts/dev_server.sh
# server will be available at http://127.0.0.1:8000/docs
```

## Notes and common issues
- We use `requirements-dev.txt` for test/dev pinning (this mirrors CI). It intentionally pins older `httpx` and `pydantic` versions that the backend tests expect (e.g. `httpx==0.23.3`, `pydantic==1.10.24`).
- If you need agent tooling (CrewAI, Chromadb, or other packages that require pydantic v2 / httpx >=0.27), create a separate venv for those tools to avoid conflicts:

```bash
python3 -m venv .venv-agents
source .venv-agents/bin/activate
pip install crewai chromadb mcp  # or other agent deps
```

- CI uses `requirements-dev.txt` (see `.github/workflows/ci.yml`) so reproducing the pinned dev env locally ensures CI parity.

## Debugging tests
- If pytest collection fails with:
  `TypeError: Client.__init__() got an unexpected keyword argument 'app'`
  then your environment likely has incompatible `httpx` / `starlette` versions. Make sure you installed `requirements-dev.txt` in the active venv and re-run `bash scripts/test_all.sh`.

- To wipe Python caches before running tests:
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Helpful commands
- Run a single backend test file:
  `pytest tests/backend/test_measure_and_recs.py -q`
- Run the TestClient smoke script (prints two endpoint outputs):
  `python3 tests/backend/test_endpoints.py`

## Links
- Pause/resume developer guide: `docs/PAUSE_RESUME_GUIDE.md`
- CI workflow (uses pinned dev deps): `.github/workflows/ci.yml`

---
Last updated: October 2025
Maintainer: Laura Tornga (@rocketroz)
