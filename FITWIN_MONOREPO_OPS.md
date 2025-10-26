# FitTwin Monorepo Ops Documentation

## GitHub Pull Request Description

### Title: Migrate FitTwin Codebase to Monorepo Structure

### Summary
This PR merges the newly migrated monorepo branch (`monorepo-migration`) into `main`. The migration consolidates backend, agents, frontend, and data into a single cohesive repository structure. All imports, dependencies, and environment configurations have been standardized. All tests have been verified as passing, and new utility scripts are included for development, testing, and agent execution.

### Key Changes
- **Reorganized file structure:** `/backend`, `/agents`, `/frontend`, `/data`, `/scripts`, `/tests`, `/docs`
- **Updated import paths:** Now use `backend.app.*` instead of legacy `src.server.*` imports
- **Added `backend/requirements.txt`** for dependency management (includes httpx for testing)
- **Created utility scripts:**
  - `scripts/dev_server.sh` - Start development server
  - `scripts/test_all.sh` - Run all unit tests
  - `scripts/run_agents.sh` - Execute CrewAI agents
- **Introduced environment templates:**
  - `backend/.env.example` - Backend configuration template
  - `agents/.env.example` - Agent configuration template
- **Updated CI/CD paths** to match new folder structure
- **Moved Supabase migrations** to `data/supabase/migrations/`
- **Organized agents** into `agents/crew/`, `agents/config/`, `agents/prompts/`, `agents/tools/`

### Testing

```bash
bash scripts/test_all.sh
```

**Result:** All tests pass (2/2 passing)

### API Verification

Both endpoints tested and working:
- ✅ `/measurements/` - Returns normalized body measurements
- ✅ `/dmaas/latest` - Returns measurements + size recommendations

### Risks
- Any external scripts or agents still referencing old file paths (`src/server/*`) must be updated
- Ensure `.env` variables match new format before deploying
- Update any CI/CD pipelines to use `backend/requirements.txt` instead of root `requirements.txt`

### Rollback Plan
- **Option 1:** Use `git checkout monorepo-migration-backup` to restore pre-migration state
- **Option 2:** Use `git reset --hard origin/main` if main merge needs to be reverted
- **Option 3:** Revert the merge commit: `git revert -m 1 <merge-commit-hash>`

### Migration Statistics
- **Files changed:** 44
- **Lines added:** 286
- **Lines removed:** 145
- **Git history:** Preserved using `git mv`

---

## GitHub Actions Workflow YAML

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ main, monorepo-migration ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run backend tests
        run: |
          export PYTHONPATH="${PYTHONPATH}:$(pwd)"
          pytest tests/backend/ -v
      
      - name: Test API endpoints
        run: |
          export PYTHONPATH="${PYTHONPATH}:$(pwd)"
          python3 tests/backend/test_endpoints.py
```

---

## Pause/Resume Guide

### Pause Active Work

1. **Commit or stash changes:**
   ```bash
   git add .
   git commit -m "pause work: [description]"
   # OR
   git stash save "WIP: [description]"
   ```

2. **Create a backup branch (optional):**
   ```bash
   git branch backup-$(date +%Y%m%d-%H%M%S)
   ```

3. **Switch back to main safely:**
   ```bash
   git checkout main
   ```

### Resume Work

1. **Pull latest updates:**
   ```bash
   git fetch origin
   git pull origin main
   ```

2. **Checkout your work branch:**
   ```bash
   git checkout monorepo-migration
   # OR restore stashed work
   git stash pop
   ```

3. **Merge or rebase as needed:**
   ```bash
   git rebase main
   # OR
   git merge main
   ```

---

## Ops Runbook (Quick Reference)

### Repository Root Layout

```
/agents       -> CrewAI multi-agent system
  /crew       -> Agent implementations
  /config     -> Agent configurations
  /prompts    -> Agent prompts
  /tools      -> Agent tools
/backend      -> FastAPI application
  /app
    /routers  -> API endpoints
    /schemas  -> Pydantic models
    /services -> Business logic
    /core     -> Configuration & utilities
/data         -> Database and data files
  /supabase
    /migrations -> SQL migration files
/docs         -> Documentation
  /runbooks   -> Operational guides
/frontend     -> UI components
  /src        -> Frontend source files
/scripts      -> Utilities & test scripts
/tests        -> Test suites
  /backend    -> Backend tests
  /agents     -> Agent tests
```

### Startup Commands

**Development Server:**
```bash
bash scripts/dev_server.sh
# OR manually:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- API: http://127.0.0.1:8000
- Swagger Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Run Tests

**All tests:**
```bash
bash scripts/test_all.sh
```

**Backend tests only:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/backend/ -v
```

**Specific test file:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/backend/test_measure_and_recs.py -v
```

### Run Agents

```bash
bash scripts/run_agents.sh
# OR manually:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 agents/crew/crew_test.py
```

### Environment Setup

**Backend:**
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Configure:
- `ENV` - Application environment (dev, test, prod)
- `VENDOR_MODE` - Vendor integration mode (stub, real)
- `SUPABASE_URL` - Supabase project URL (if using)
- `SUPABASE_KEY` - Supabase API key (if using)

**Agents:**
```bash
cp agents/.env.example agents/.env
nano agents/.env
```

Configure:
- `OPENAI_API_KEY` - OpenAI API key for CrewAI
- `AGENT_MODEL` - LLM model (e.g., gpt-4)
- `AGENT_TEMPERATURE` - Temperature setting

### Database Migrations

**Apply Supabase migrations:**
```bash
# Using Supabase CLI
supabase db push

# OR manually
psql -f data/supabase/migrations/init_schema.sql
psql -f data/supabase/migrations/init_rls.sql
```

### Deployment Notes

**Prerequisites:**
- Python 3.11+
- All dependencies in `backend/requirements.txt` installed
- Environment variables configured in `.env` files

**CI/CD:**
- Workflow validates compatibility with Python 3.11
- Tests run on every push to main and pull requests
- Use `backend/requirements.txt` for dependency installation

**Environment Variables:**
- Never commit `.env` files to Git
- Use `.env.example` templates for reference
- Set production secrets in deployment platform

### Rollback Commands

**Rollback to pre-migration state:**
```bash
git checkout monorepo-migration-backup
```

**Revert main branch:**
```bash
git checkout main
git reset --hard origin/main
```

**Revert specific merge:**
```bash
git revert -m 1 <merge-commit-hash>
git push origin main
```

---

## Common Operations

### Adding New API Endpoint

1. Create router file in `backend/app/routers/`
2. Define endpoint using FastAPI decorators
3. Import and include router in `backend/app/main.py`
4. Add tests in `tests/backend/`

### Adding New Agent

1. Create agent file in `agents/crew/`
2. Add configuration in `agents/config/`
3. Define prompts in `agents/prompts/`
4. Add custom tools in `agents/tools/`
5. Update `scripts/run_agents.sh` if needed

### Updating Dependencies

**Backend:**
```bash
pip install <package>
pip freeze | grep <package> >> backend/requirements.txt
```

**Verify:**
```bash
pip install -r backend/requirements.txt
bash scripts/test_all.sh
```

### Creating New Migration

```bash
# Create SQL file
nano data/supabase/migrations/$(date +%Y%m%d)_description.sql

# Test locally
psql -f data/supabase/migrations/$(date +%Y%m%d)_description.sql

# Apply via Supabase CLI
supabase db push
```

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:** Update imports to use new paths:
```python
# OLD
from src.server.main import app

# NEW
from backend.app.main import app
```

### Test Failures

**Problem:** Tests can't find modules

**Solution:** Set PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/backend/ -v
```

### Missing Dependencies

**Problem:** `ModuleNotFoundError: No module named 'httpx'`

**Solution:** Install from requirements:
```bash
pip install -r backend/requirements.txt
```

### Environment Variables Not Loading

**Problem:** Settings not being read

**Solution:** Check `.env` file location and format:
```bash
# Ensure .env is in correct directory
ls -la backend/.env
ls -la agents/.env

# Check format (no spaces around =)
cat backend/.env
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review and merge dependabot PRs
- Check test coverage
- Review error logs

**Monthly:**
- Update dependencies
- Review and clean up old branches
- Backup database

**Quarterly:**
- Security audit
- Performance review
- Documentation update

### Monitoring

**Health Check:**
```bash
curl http://127.0.0.1:8000/measurements/
```

**Logs:**
```bash
# Development server logs
tail -f logs/dev.log

# Test logs
pytest tests/backend/ -v --log-cli-level=INFO
```

---

## Contact & Support

**Repository:** https://github.com/rocketroz/fitwin-crewai  
**Author:** Laura Tornga (@rocketroz)  
**Documentation:** See `/docs` directory for additional guides

---

**Last Updated:** October 25, 2025  
**Version:** Monorepo v1.0

