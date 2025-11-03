# FitTwin Monorepo

**Author:** Laura Tornga (@rocketroz)

Unified workspace for the FitTwin MediaPipe MVP: FastAPI backend, CrewAI agents, Supabase migrations, and both the current capture stub and the legacy Manus web app. The backend now exposes the DMaaS `/measurements/validate` and `/measurements/recommend` endpoints described in the FitTwin spec (see `docs/spec`).

## Project Structure

```
fitwin-crewai/
├── agents/              # CrewAI multi-agent system
│   ├── crew/           # Agent implementations
│   ├── config/         # Agent configurations
│   ├── prompts/        # Agent prompts
│   └── tools/          # Agent tools
├── backend/            # FastAPI backend application
│   └── app/
│       ├── routers/    # API endpoints
│       ├── schemas/    # Pydantic models
│       ├── services/   # Business logic
│       └── core/       # Configuration and utilities
├── data/               # Data and database files
│   └── supabase/
│       ├── migrations/ # Database migrations
│       └── sql/        # SQL scripts
├── docs/               # Documentation
│   ├── runbooks/       # Operational guides
│   └── PAUSE_RESUME_GUIDE.md
├── frontend/           # Frontend application
│   ├── src/            # Current capture stub
│   └── legacy_web_app/ # Manus Vite/React implementation package
├── scripts/            # Utility scripts
├── tests/              # Test suites
│   ├── backend/        # Backend tests
│   └── agents/         # Agent tests
└── README.md
```

## Quick Start

See `AGENTS.md` for contributor guidelines, coding conventions, and PR expectations that apply across the monorepo.

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/rocketroz/fitwin-crewai.git
cd fitwin-crewai

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Dev environment (recommended)

For repeatable local testing and development (tests were validated with these pins), create and use a dev requirements file. This avoids accidental upgrades of transitive packages that can break the TestClient/Test dependencies.

```bash
# Create and activate venv (if you haven't already)
python3 -m venv .venv
source .venv/bin/activate

# Install pinned dev/test dependencies
pip install -r requirements-dev.txt

# Run tests
bash scripts/test_all.sh
```

Note: `requirements-dev.txt` pins the FastAPI/Pydantic 2 stack used by CI (currently `fastapi==0.115.0`, `pydantic==2.9.2`, `httpx==0.27.2`) along with linting tools. If you need a different toolchain (for example experimental CrewAI releases), create a separate virtual environment to avoid dependency conflicts.

### 2. Configuration

```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp agents/.env.example agents/.env

# Edit the .env files with your configuration
```

### 3. Run the Backend

```bash
# Using the convenience script
bash scripts/dev_server.sh

# Or manually
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000/docs` (Swagger UI).

### 4. Run Tests

```bash
# Run all tests
bash scripts/test_all.sh

# Or run specific test suites
pytest tests/backend/ -v
```

### 5. Run Agents

```bash
# Run CrewAI agents
bash scripts/run_agents.sh
```

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

### Health probes

- `GET /` — Lightweight readiness message with docs pointer.
- `GET /health` — Basic health status payload (extend with database checks as needed).

## Environment Variables

### Backend (`backend/.env`)

- `ENV` - Application environment (dev, test, prod). Default: `dev`
- `VENDOR_MODE` - Vendor integration mode (`stub` or `real`). Default: `stub`

### Agents (`agents/.env`)

- `OPENAI_API_KEY` - OpenAI API key for CrewAI agents
- `AGENT_MODEL` - LLM model to use (e.g., `gpt-4`)
- `AGENT_TEMPERATURE` - Temperature setting for agent responses

## Development Guide

### Vendor Integration

Implement real vendor integration in `backend/app/services/vendor_client.py`:

```python
def fetch_real_vendor(session_id: str) -> dict:
    # Replace with actual vendor API call
    response = requests.post(VENDOR_API_URL, json={"session_id": session_id})
    return response.json()
```

Then set `VENDOR_MODE=real` in your environment.

### Normalization

Add custom mappers in `backend/app/core/utils.py` if vendors introduce new measurement fields.

### Fit Rules

Enhance size recommendation logic in:
- `backend/app/services/fit_rules_tops.py` - Top garment sizing
- `backend/app/services/fit_rules_bottoms.py` - Bottom garment sizing

Replace placeholder logic with actual size charts, ease calculations, and comprehensive unit tests.

### Agent Development

Add new agents in `agents/crew/` and configure them in `agents/config/`.

## Testing

The project uses pytest for testing. Test files are organized by component:

- `tests/backend/` - Backend API and service tests
- `tests/agents/` - Agent behavior and integration tests

Run tests with:

```bash
pytest tests/ -v
```

## Database Migrations

Supabase migrations are stored in `data/supabase/migrations/`. To apply migrations:

```bash
# Using Supabase CLI
supabase db push

# Or manually execute SQL files
psql -f data/supabase/migrations/init_schema.sql
psql -f data/supabase/migrations/init_rls.sql
```

## Documentation

Additional documentation is available in the `docs/` directory:

- [Pause/Resume Guide](docs/PAUSE_RESUME_GUIDE.md) - Guide for pausing and resuming work
- [Legacy README](docs/README_legacy.md) - Original project documentation
- [`docs/spec`](docs/spec) - Manus spec kit, including deployment guide, environment template, and the PDF reference (`speckit_v2.pdf`)

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the project structure
3. Add tests for new functionality
4. Run the test suite to ensure everything passes
5. Submit a pull request

## License

See [LICENSE](LICENSE) for details.

## Version History

- **Monorepo Migration** - Reorganized into monorepo structure with separate backend, agents, and frontend
- **baseline/v1.0** - Initial release with basic measurement and recommendation API

## Rollback

To rollback to the pre-monorepo structure:

```bash
git checkout baseline/v1.0
```

## Support

For issues, questions, or contributions, please open an issue on GitHub.

