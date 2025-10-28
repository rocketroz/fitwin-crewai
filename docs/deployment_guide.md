# FitTwin DMaaS API - Deployment Guide

This guide captures the Manus deployment walkthrough, adapted for the monorepo.

**Author:** Manus AI  
**Date:** October 27, 2025

## 1. Prerequisites

Install:

- Python 3.11+
- Node.js 18+ (for Supabase CLI)
- Git
- Docker (optional for local runs)

## 2. Local Development Setup

### 2.1 Clone the Repository

```bash
git clone https://github.com/your-username/fitwin-crewai.git
cd fitwin-crewai
```

### 2.2 Set Up Supabase

1. Create a Supabase project and note the Project URL, anon key, and service_role key.
2. Run migrations from `data/supabase/migrations` in order (see Supabase README).
3. Create a private storage bucket named `measurement-photos`.

### 2.3 Configure Environment Variables

```bash
cp .env.example .env
```

Populate `.env` with Supabase and API credentials:

```ini
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-service-role-key>
SUPABASE_ANON_KEY=<your-anon-key>
API_KEY=staging-secret-key
API_BASE_URL=http://localhost:8000
OPENAI_API_KEY=<your-openai-api-key>
AGENT_MODEL=gpt-4o-mini
X_API_KEY=staging-secret-key
```

### 2.4 Install Dependencies and Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Run the agents:

```bash
python agents/crew/measurement_crew.py
```

## 3. Testing

```bash
source .venv/bin/activate
pytest tests/backend/
pytest tests/agents/
```

## 4. Production Deployment

### 4.1 GitHub Secrets

Set secrets under Settings → Secrets → Actions:

- `SUPABASE_ACCESS_TOKEN`
- `SUPABASE_PROJECT_ID`
- `OPENAI_API_KEY`

### 4.2 Deploy to Supabase

The workflow `.github/workflows/backend-ci.yml` runs tests and applies migrations on pushes to `main`. Host the FastAPI service via Supabase Edge Functions, Vercel, Railway, or similar.

### 4.3 Five-Day MVP Timeline

- **Day 1:** Architecture & data foundation
- **Day 2:** Core MediaPipe measurement logic
- **Day 3:** End-to-end data flow (photo upload + recommendations)
- **Day 4:** API hardening & security
- **Day 5:** Testing, TestFlight build, go-live review

## 5. Cost Management

- Target MVP cost: $0–$200 using free tiers.
- Ongoing: <$20/month.
- Monitor Supabase usage to stay within budget.

## 6. Next Steps

- Validate accuracy with tape-measure benchmarks.
- Launch DMaaS beta with pilot customers.
- Collect data to train proprietary sizing models.

Refer to `docs/speckit.md` for the comprehensive technical specification.
