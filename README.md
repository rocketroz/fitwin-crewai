# FitTwin Monorepo

**Author:** Laura Tornga (@rocketroz)

A comprehensive monorepo for the FitTwin project, including backend API, CrewAI agents, frontend components, and data management. The backend provides two-photo measurement mapping for upper and lower body with normalized body measurement schema and size recommendations.

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
│   └── src/
├── scripts/            # Utility scripts
├── tests/              # Test suites
│   ├── backend/        # Backend tests
│   └── agents/         # Agent tests
└── README.md
```

## Quick Start

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

### Measurements Endpoint

```bash
curl -s http://127.0.0.1:8000/measurements/ | python -m json.tool
```

Returns normalized body measurements from the vendor API.

### DMaaS (Digital Measurement as a Service) Endpoint

```bash
curl -s http://127.0.0.1:8000/dmaas/latest | python -m json.tool
```

Returns measurements plus size recommendations for tops and bottoms.

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

