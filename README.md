# FitTwin Monorepo

**Author:** Laura Tornga (@rocketroz)

Unified workspace for the FitTwin MediaPipe MVP: FastAPI backend, CrewAI agents, Supabase migrations, and both the current capture stub and the legacy Manus web app. The backend now exposes the DMaaS `/measurements/validate` and `/measurements/recommend` endpoints described in the FitTwin spec (see `docs/spec`).

## Project Structure

```
fitwin-crewai/
├── agents/                # CrewAI multi-agent system
│   ├── crew/              # Agent implementations (includes Manus measurement crew)
│   ├── config/            # Agent configurations
│   ├── prompts/           # Prompt assets
│   └── tools/             # Shared CrewAI tools (retry & circuit breaker logic)
├── backend/               # FastAPI backend application
│   └── app/
│       ├── core/          # Config + validation helpers
│       ├── routers/       # API endpoints (MediaPipe DMaaS routes)
│       ├── schemas/       # Pydantic models and error envelopes
│       └── services/      # Fit rule placeholders and vendor glue
├── data/                  # Database and Supabase assets
│   └── supabase/
│       ├── migrations/    # Init + measurement provenance migrations
│       └── README.md      # Supabase setup guide
├── docs/
│   ├── runbooks/          # Operational guides
│   ├── spec/              # Manus spec-kit (speckit, deployment guide, env template)
│   └── PAUSE_RESUME_GUIDE.md
├── frontend/
│   ├── src/               # Current capture stub
│   └── legacy_web_app/    # Manus Vite/React implementation package
├── scripts/               # Helper scripts (dev server, test runner, agents)
├── tests/
│   ├── backend/           # Backend / FastAPI tests (validate + recommend flows)
│   └── agents/            # CrewAI tool tests with mocks
└── CHANGELOG.md

## Quick Start

See `AGENTS.md` for contributor guidelines, coding conventions, and PR expectations that apply across the monorepo.

### 1. Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Note: `requirements-dev.txt` pins the FastAPI/Pydantic 2 stack used by CI (currently `fastapi==0.115.0`, `pydantic==2.9.2`, `httpx==0.27.2`) along with linting tools. If you need a different toolchain (for example experimental CrewAI releases), create a separate virtual environment to avoid dependency conflicts.

### 1a. Environment (legacy Manus instructions)

If you prefer to mirror the legacy Manus workflow verbatim, the same steps are available in condensed form:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

These commands are preserved for downstream merges so the Manus documentation diff stays minimal.

### 2. Configuration

```bash
cp backend/.env.example backend/.env
cp agents/.env.example agents/.env
```

Populate the following values:

- `API_KEY` — Shared secret for `/measurements/*` requests (defaults to `staging-secret-key`).
- Supabase credentials (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) if you plan to run migrations or store provenance data.
- Agent secrets (`OPENAI_API_KEY`, etc.) for CrewAI flows.

### 3. Run the Backend

```bash
bash scripts/dev_server.sh
# or
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger UI: <http://127.0.0.1:8000/docs>

### 4. Tests

```bash
bash scripts/test_all.sh          # Runs backend + agent suites
pytest tests/backend/ -v          # Backend only
pytest tests/agents/ -v           # Agent tool mocks
```

## Reference Documentation

- `docs/spec/speckit.md` / `speckit_v2.pdf` — Full MediaPipe MVP technical spec.
- `docs/spec/deployment_guide.md` — Step-by-step deployment playbook.
- `docs/spec/ENV_TEMPLATE.md` — Environment variable template used in Manus package.
- `docs/spec/README.manus.md` — Original Manus package README for historical context.

## API Endpoints

All measurement routes require an `X-API-Key` header (default: `staging-secret-key`).

### Validate measurements

```bash
curl -s -X POST \
    http://127.0.0.1:8000/measurements/validate \
    -H "Content-Type: application/json" \
    -H "X-API-Key: staging-secret-key" \
    -d '{"waist_natural": 32, "hip_low": 40, "unit": "in", "session_id": "readme-demo"}' \
    | python -m json.tool
```

Returns normalized centimeter measurements, a confidence score, and provenance IDs. When landmarks are provided, the placeholder MediaPipe calculation scaffold runs until production geometry equations are wired in.

**Legacy curl example (single-line format)**

```bash
curl -s -X POST http://127.0.0.1:8000/measurements/validate \
    -H "Content-Type: application/json" \
    -H "X-API-Key: staging-secret-key" \
    -d '{"waist_natural": 32, "hip_low": 40, "unit": "in", "session_id": "readme-demo"}' \
    | python -m json.tool
```

### Recommend sizes

```bash
curl -s -X POST \
    http://127.0.0.1:8000/measurements/recommend \
    -H "Content-Type: application/json" \
    -H "X-API-Key: staging-secret-key" \
    -d '{"waist_natural_cm": 81.28, "hip_low_cm": 101.6, "chest_cm": 101.6, "model_version": "v1.0-mediapipe"}' \
    | python -m json.tool
```

Returns stubbed recommendations (tops + bottoms) alongside the processed measurement payload. Replace the placeholder logic in `backend/app/routers/measurements.py` and the fit-rule services as real sizing charts become available.

**Legacy curl example (single-line format)**

```bash
curl -s -X POST http://127.0.0.1:8000/measurements/recommend \
    -H "Content-Type: application/json" \
    -H "X-API-Key: staging-secret-key" \
    -d '{"waist_natural_cm": 81.28, "hip_low_cm": 101.6, "chest_cm": 101.6, "model_version": "v1.0-mediapipe"}' \
    | python -m json.tool
```

### Health probes

- `GET /` — Lightweight readiness message with docs pointer.
- `GET /health` — Basic health status payload (extend with database checks as needed).

## Frontend

- `frontend/src/photoCaptureStub.js` — Lightweight stub used during Codex development.
- `frontend/legacy_web_app/` — Manus Vite/React implementation (camera flows, TODOs, package.json). Use `pnpm install` inside that folder to run the full experience.

## Agents

- `agents/tools/measurement_tools.py` — Validate/recommend tools with timeout, retry, and circuit breaker logic.
- `agents/crew/measurement_crew.py` — Five-agent crew (CEO, Architect, ML Engineer, DevOps, Reviewer) reflecting the spec’s directives.

Run the crew locally:

```bash
source .venv/bin/activate
python agents/crew/measurement_crew.py
```

## Database / Supabase

1. `supabase db push` (or run SQL files manually) to apply `init_schema`, `init_rls`, and `002_measurement_provenance.sql`.
2. Ensure a storage bucket exists for photo uploads if you intend to capture provenance.
3. RLS policies restrict access to user-owned rows; service role has full read/write for DMaaS operations.

See `data/supabase/README.md` for configuration details.

## Testing & CI

- `scripts/test_all.sh` calls the backend pytest suite plus agent unit tests.
- GitHub Actions workflow (`.github/workflows/ci.yml`) installs `requirements-dev.txt`, runs backend tests, and exercises the Python CLI smoke tests. Extend with lint or Supabase deploy steps as needed (the legacy Manus workflow is preserved in `docs/spec/README.manus.md`).

## Changelog

Legacy Manus changelog is available at `CHANGELOG.md`. Record new entries using the same format (date + summary).

## Next Steps

- Replace placeholder geometry in `backend/app/core/validation.py` with real MediaPipe calculations.
- Wire production fit rules into `backend/app/routers/measurements.py` (or dedicated services).
- Decide whether the Manus web app becomes the primary frontend or remains archived.
- Integrate Supabase migrations into CI/CD if automatic deploys are required.
