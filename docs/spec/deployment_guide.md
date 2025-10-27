'''
# FitTwin DMaaS API - Deployment Guide

This guide provides step-by-step instructions for deploying the FitTwin DMaaS API, including local setup, database configuration, and production deployment.

**Author:** Manus AI
**Date:** October 27, 2025

## 1. Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**
- **Node.js 18+** (for Supabase CLI)
- **Git**
- **Docker** (optional, for local development)

## 2. Local Development Setup

### 2.1. Clone the Repository

```bash
# Clone your forked repository
git clone https://github.com/your-username/fitwin-crewai.git
cd fitwin-crewai

# Copy the implementation files from the provided zip package
# into the repository, overwriting existing files if necessary.
```

### 2.2. Set Up Supabase

1.  **Create a Supabase Project:**
    -   Go to [supabase.com](https://supabase.com) and create a new project.
    -   Note your **Project URL**, **anon key**, and **service_role key** from **Settings > API**.

2.  **Run Database Migrations:**
    -   Navigate to **SQL Editor** in your Supabase dashboard.
    -   Open `data/supabase/migrations/002_measurement_provenance.sql` from the implementation package.
    -   Copy and paste the entire SQL script into the SQL Editor and click **Run**.

3.  **Create Storage Bucket:**
    -   Navigate to **Storage**.
    -   Create a new bucket named `measurement-photos`.
    -   Keep it private (uncheck "Public bucket").

### 2.3. Configure Environment Variables

1.  Copy the environment variables template:

    ```bash
    cp .env.example .env
    ```

2.  Edit the `.env` file and add your Supabase and OpenAI credentials:

    ```ini
    # Supabase Configuration
    SUPABASE_URL=https://<your-project-ref>.supabase.co
    SUPABASE_KEY=<your-service-role-key>
    SUPABASE_ANON_KEY=<your-anon-key>

    # API Configuration
    API_KEY=staging-secret-key
    API_BASE_URL=http://localhost:8000

    # Agent Configuration
    OPENAI_API_KEY=<your-openai-api-key>
    AGENT_MODEL=gpt-4o-mini
    X_API_KEY=staging-secret-key
    ```

### 2.4. Install Dependencies and Run

1.  Create a virtual environment and install dependencies:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r backend/requirements.txt
    ```

2.  Run the FastAPI backend locally:

    ```bash
    uvicorn backend.app.main:app --reload
    ```

    The API will be available at `http://localhost:8000`.

3.  Run the agent system:

    ```bash
    python agents/crew/measurement_crew.py
    ```

## 3. Testing

Run the backend and agent tests to ensure everything is working correctly:

```bash
# Ensure you are in the virtual environment
source venv/bin/activate

# Run backend tests
pytest tests/backend/

# Run agent tests
pytest tests/agents/
```

All tests should pass.

## 4. Production Deployment

### 4.1. Configure GitHub Secrets

In your GitHub repository, go to **Settings > Secrets and variables > Actions** and add the following secrets:

-   `SUPABASE_ACCESS_TOKEN`: Your Supabase personal access token.
-   `SUPABASE_PROJECT_ID`: Your Supabase project ID.
-   `OPENAI_API_KEY`: Your OpenAI API key.

### 4.2. Deploy to Supabase

The included GitHub Actions workflow (`.github/workflows/backend-ci.yml`) will automatically run tests and deploy the database migrations to Supabase when you push to the `main` branch.

To deploy the backend API, you can use Supabase Edge Functions or another hosting provider like Vercel or Railway.

### 4.3. Five-Day MVP Timeline

Follow the 5-day timeline outlined in `speckit.md` to complete the MVP:

-   **Day 1:** Architecture & Data Foundation (Supabase schema, repo scaffolding)
-   **Day 2:** Core Measurement Logic (MediaPipe integration, validation endpoint)
-   **Day 3:** End-to-End Data Flow (Photo upload, recommendation endpoint)
-   **Day 4:** API & Security (API docs, RLS policies, security review)
-   **Day 5:** Testing & Deployment (Tape-measure benchmarks, TestFlight deployment)

## 5. Cost Management

-   **MVP Cost:** $0-$200 (depending on optional vendor calibration).
-   **Ongoing Cost:** <$20/month (if staying on free tiers).
-   Monitor usage in your Supabase dashboard to avoid unexpected costs.

## 6. Next Steps

-   **Accuracy Validation:** Conduct tape-measure benchmarks to validate MediaPipe accuracy.
-   **DMaaS Launch:** Onboard your first AI/retailer customers.
-   **Proprietary Model:** Collect data to train your own proprietary measurement model.

---

This guide provides a comprehensive overview of the deployment process. For more detailed technical specifications, refer to `speckit.md`.
'''
