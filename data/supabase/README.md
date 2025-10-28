# Supabase Setup

1. Create a new Supabase project and enable the Postgres extensions:
   - `uuid-ossp` for UUID generation
   - `pgcrypto` if you plan to hash personally identifiable data
2. Apply migrations in `data/supabase/migrations/` in order:
   ```bash
   psql $SUPABASE_DB_URL -f data/supabase/migrations/init_schema.sql
   psql $SUPABASE_DB_URL -f data/supabase/migrations/init_rls.sql
   psql $SUPABASE_DB_URL -f data/supabase/migrations/002_measurement_provenance.sql
   ```
3. Configure RLS policies so agent and backend access is limited:
   - Restrict read/write to service role for ingestion.
   - Create limited tokens for analytics consumers.
4. Store Supabase credentials in `backend/.env` and `agents/.env`.

Refer to `deployment_guide.md` for end-to-end deployment instructions.
