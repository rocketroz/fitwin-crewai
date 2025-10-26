-- Minimal demo schema (local reference)
create table if not exists measurements (
  id serial primary key,
  user_id text,
  data jsonb,
  created_at timestamptz default now()
);
