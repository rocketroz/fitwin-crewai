# Environment Variables Template

This file documents the required environment variables for the FitTwin Three-Mode Platform.

## Backend API Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```bash
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

## Web App Environment Variables

Create a `.env` file in the `web-app/` directory with the following variables:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_KEY=staging-secret-key

# App Configuration
VITE_APP_TITLE=FitTwin Web App
VITE_APP_LOGO=/logo.svg
```

## GitHub Actions Secrets

Add the following secrets to your GitHub repository:
- Settings → Secrets and variables → Actions → New repository secret

```
SUPABASE_ACCESS_TOKEN=<your-supabase-access-token>
SUPABASE_PROJECT_ID=<your-supabase-project-id>
OPENAI_API_KEY=<your-openai-api-key>
```

## How to Obtain Credentials

### Supabase
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Navigate to **Settings → API**
3. Copy:
   - Project URL → `SUPABASE_URL`
   - anon/public key → `SUPABASE_ANON_KEY`
   - service_role key → `SUPABASE_KEY`

### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com)
2. Navigate to **API keys**
3. Create a new API key → `OPENAI_API_KEY`

### API Key
- Generate a secure random string for `API_KEY`
- Use the same value for `X_API_KEY` in agent configuration
- Example: `openssl rand -hex 32`

## Security Notes

- **NEVER commit `.env` files to version control**
- Add `.env` to your `.gitignore` file
- Use different keys for development, staging, and production
- Rotate keys regularly
- Use GitHub Actions secrets for CI/CD
- Keep service role keys secure (they bypass Row Level Security)

## Quick Setup Script

```bash
# Copy this template
cp ENV_TEMPLATE.md .env

# Edit with your credentials
nano .env

# Or use environment variables
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="your-service-role-key"
export OPENAI_API_KEY="your-openai-key"
```

