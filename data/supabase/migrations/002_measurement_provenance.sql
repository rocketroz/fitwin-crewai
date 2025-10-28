-- Supabase migration for measurement provenance storage (Manus package).

create table if not exists measurement_sessions (
    id uuid primary key default uuid_generate_v4(),
    session_id text unique not null,
    source_type text default 'mediapipe_web',
    platform text default 'web_mobile',
    device_id text,
    front_photo_url text,
    side_photo_url text,
    created_at timestamptz default timezone('utc', now())
);

create table if not exists mediapipe_landmarks (
    id uuid primary key default uuid_generate_v4(),
    session_id text not null references measurement_sessions(session_id) on delete cascade,
    view text not null check (view in ('front', 'side')),
    landmarks jsonb not null,
    image_width integer,
    image_height integer,
    timestamp timestamptz,
    created_at timestamptz default timezone('utc', now())
);

create table if not exists normalized_measurements (
    id uuid primary key default uuid_generate_v4(),
    session_id text not null references measurement_sessions(session_id) on delete cascade,
    payload jsonb not null,
    source text default 'mediapipe',
    model_version text default 'v1.0-mediapipe',
    confidence numeric,
    accuracy_estimate numeric,
    created_at timestamptz default timezone('utc', now())
);

create index if not exists idx_measurement_sessions_created_at on measurement_sessions(created_at);
create index if not exists idx_mediapipe_landmarks_session_view on mediapipe_landmarks(session_id, view);
create index if not exists idx_normalized_measurements_session on normalized_measurements(session_id);

comment on table measurement_sessions is 'Stores high-level session metadata and provenance.';
comment on table mediapipe_landmarks is 'Stores raw MediaPipe landmark payloads for replay/calibration.';
comment on table normalized_measurements is 'Stores normalized measurement outputs with accuracy metadata.';
