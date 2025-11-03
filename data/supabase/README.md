# Supabase Setup

1. Create a new Supabase project and enable the Postgres extensions:
   - `uuid-ossp` for UUID generation
   - `pgcrypto` if you plan to hash personally identifiable data
2. Apply migrations in `data/supabase/migrations/` in order:
   ```bash
   psql "$SUPABASE_DB_URL" -f data/supabase/migrations/init_schema.sql
   psql "$SUPABASE_DB_URL" -f data/supabase/migrations/init_rls.sql
   psql "$SUPABASE_DB_URL" -f data/supabase/migrations/002_measurement_provenance.sql
   ```
3. Configure RLS policies so agent and backend access is limited:
   - Restrict read/write to the service role for ingestion.
   - Create limited tokens for analytics consumers.
4. Store Supabase credentials in both `backend/.env` and `agents/.env`.

Refer to `docs/spec/deployment_guide.md` for end-to-end deployment instructions and CI/CD hooks.
# Supabase Configuration for FitTwin MVP

This directory contains database migrations and configuration for the FitTwin DMaaS API.

## Setup Instructions

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Enter project details:
   - **Name:** FitTwin MVP
   - **Database Password:** (generate a strong password)
   - **Region:** Choose closest to your users
4. Click "Create new project"

### 2. Run Database Migrations

#### Option A: Using Supabase Dashboard (Recommended for MVP)

1. Open your project in Supabase Dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click "New Query"
4. Copy and paste the contents of `migrations/002_measurement_provenance.sql`
5. Click "Run" to execute the migration
6. Verify that all tables were created successfully

#### Option B: Using Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref <your-project-ref>

# Run migrations
supabase db push
```

### 3. Configure Storage for Photos

1. Navigate to **Storage** in the Supabase Dashboard
2. Click "Create a new bucket"
3. Enter bucket details:
   - **Name:** `measurement-photos`
   - **Public bucket:** No (keep private)
   - **File size limit:** 10 MB
4. Click "Create bucket"
5. Set up RLS policies for the bucket:
   - Users can upload their own photos
   - Service role can access all photos

### 4. Get API Credentials

1. Navigate to **Settings** → **API** in the Supabase Dashboard
2. Copy the following credentials:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon/public key:** For client-side authentication
   - **service_role key:** For backend API (keep secret!)

### 5. Configure Environment Variables

Add the following environment variables to your backend `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here

# API Configuration
API_KEY=staging-secret-key
API_BASE_URL=http://localhost:8000

# Agent Configuration
OPENAI_API_KEY=your-openai-key-here
AGENT_MODEL=gpt-4o-mini
X_API_KEY=staging-secret-key
```

## Database Schema Overview

The migration creates the following tables:

### Core Tables

- **measurement_sessions**: Tracks measurement sessions with accuracy estimates
- **measurement_photos**: Stores raw photos for provenance and model training
- **mediapipe_landmarks**: Stores MediaPipe Pose landmarks
- **measurements_mediapipe**: Stores calculated measurements from landmarks
- **size_recommendations**: Stores size recommendations

### Calibration Table

- **measurements_vendor**: Stores vendor API measurements for calibration only (excluded from live)

## Row Level Security (RLS)

All tables have RLS enabled with the following policies:

- **Users**: Can only access their own data
- **Service role**: Can access all data (for DMaaS API)
- **Vendor measurements**: Only accessible by service role

## Testing the Setup

Run the following SQL query to verify the schema:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'measurement%';
```

You should see 6 tables listed.

## Cost Estimate

With Supabase free tier:
- **Database storage:** 500 MB (sufficient for ~1,000 sessions)
- **Bandwidth:** 2 GB/month
- **Storage:** 1 GB (sufficient for ~200 photo pairs)

**Total cost:** $0/month for MVP

## Next Steps

1. Test the backend API with Supabase integration
2. Implement photo upload to Supabase Storage
3. Add database triggers for provenance tracking
4. Set up monitoring and logging

