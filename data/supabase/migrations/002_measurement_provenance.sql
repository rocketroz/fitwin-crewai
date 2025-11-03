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
-- Migration: Measurement Provenance Schema
-- Description: Create tables for storing measurement provenance, including raw photos,
--              MediaPipe landmarks, calculated measurements, and size recommendations.
-- Date: 2025-10-27
-- Author: Manus AI

-- Measurement sessions table
CREATE TABLE measurement_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id),
    session_id TEXT UNIQUE NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'mediapipe_web', -- arkit_lidar, mediapipe_native, mediapipe_web, user_input
    platform TEXT NOT NULL DEFAULT 'web_mobile', -- ios, android, web_mobile, web_desktop
    device_id TEXT,
    front_photo_url TEXT,
    side_photo_url TEXT,
    browser_info JSONB,
    processing_location TEXT, -- client, server
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'pending', -- pending, completed, failed
    accuracy_estimate FLOAT,
    needs_calibration BOOLEAN DEFAULT FALSE
);

-- Raw photos table
CREATE TABLE measurement_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES measurement_sessions(id) ON DELETE CASCADE,
    photo_type TEXT NOT NULL, -- front, side
    photo_url TEXT NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_width INT,
    image_height INT
);

-- MediaPipe landmarks table
CREATE TABLE mediapipe_landmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES measurement_sessions(id) ON DELETE CASCADE,
    photo_id UUID REFERENCES measurement_photos(id) ON DELETE CASCADE,
    landmark_type TEXT NOT NULL, -- front, side
    landmarks JSONB NOT NULL, -- Array of {x, y, z, visibility}
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_version TEXT DEFAULT 'v3.1'
);

-- Calculated measurements table (MediaPipe-derived)
CREATE TABLE measurements_mediapipe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES measurement_sessions(id) ON DELETE CASCADE,
    height_cm FLOAT NOT NULL,
    neck_cm FLOAT,
    shoulder_cm FLOAT,
    chest_cm FLOAT,
    underbust_cm FLOAT,
    waist_natural_cm FLOAT,
    sleeve_cm FLOAT,
    bicep_cm FLOAT,
    forearm_cm FLOAT,
    hip_low_cm FLOAT,
    thigh_cm FLOAT,
    knee_cm FLOAT,
    calf_cm FLOAT,
    ankle_cm FLOAT,
    front_rise_cm FLOAT,
    back_rise_cm FLOAT,
    inseam_cm FLOAT,
    outseam_cm FLOAT,
    confidence FLOAT DEFAULT 1.0,
    accuracy_estimate FLOAT,
    model_version TEXT DEFAULT 'v1.0-mediapipe',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vendor measurements table (for calibration only, if needed)
CREATE TABLE measurements_vendor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES measurement_sessions(id) ON DELETE CASCADE,
    vendor_name TEXT NOT NULL, -- 3dlook, nettelo, etc.
    vendor_version TEXT,
    measurements JSONB NOT NULL, -- Raw vendor JSON response
    confidence FLOAT,
    cost_usd FLOAT,
    called_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_for_calibration BOOLEAN DEFAULT TRUE,
    excluded_from_live BOOLEAN DEFAULT TRUE -- Never use in production
);

-- Size recommendations table
CREATE TABLE size_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES measurement_sessions(id) ON DELETE CASCADE,
    measurement_id UUID REFERENCES measurements_mediapipe(id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- tops, bottoms, dresses, etc.
    size TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    rationale TEXT,
    model_version TEXT DEFAULT 'v1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_sessions_user ON measurement_sessions(user_id);
CREATE INDEX idx_sessions_session_id ON measurement_sessions(session_id);
CREATE INDEX idx_photos_session ON measurement_photos(session_id);
CREATE INDEX idx_landmarks_session ON mediapipe_landmarks(session_id);
CREATE INDEX idx_measurements_session ON measurements_mediapipe(session_id);
CREATE INDEX idx_vendor_session ON measurements_vendor(session_id);
CREATE INDEX idx_recommendations_session ON size_recommendations(session_id);

-- Row Level Security (RLS) policies
ALTER TABLE measurement_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurement_photos ENABLE ROW LEVEL SECURITY;
ALTER TABLE mediapipe_landmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurements_mediapipe ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurements_vendor ENABLE ROW LEVEL SECURITY;
ALTER TABLE size_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE normalized_measurements ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can view own sessions" ON measurement_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions" ON measurement_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own photos" ON measurement_photos
    FOR SELECT USING (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own photos" ON measurement_photos
    FOR INSERT WITH CHECK (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can view own landmarks" ON mediapipe_landmarks
    FOR SELECT USING (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own landmarks" ON mediapipe_landmarks
    FOR INSERT WITH CHECK (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can view own measurements" ON measurements_mediapipe
    FOR SELECT USING (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own measurements" ON measurements_mediapipe
    FOR INSERT WITH CHECK (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can view own recommendations" ON size_recommendations
    FOR SELECT USING (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own recommendations" ON size_recommendations
    FOR INSERT WITH CHECK (
        session_id IN (SELECT id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can view own normalized measurements" ON normalized_measurements
    FOR SELECT USING (
        session_id IN (SELECT session_id FROM measurement_sessions WHERE user_id = auth.uid())
    );

CREATE POLICY "Users can insert own normalized measurements" ON normalized_measurements
    FOR INSERT WITH CHECK (
        session_id IN (SELECT session_id FROM measurement_sessions WHERE user_id = auth.uid())
    );

-- Vendor measurements are only accessible by service role (for calibration)
CREATE POLICY "Service role full access vendor" ON measurements_vendor
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- API service role can access all data (for DMaaS API)
CREATE POLICY "Service role full access sessions" ON measurement_sessions
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access photos" ON measurement_photos
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access landmarks" ON mediapipe_landmarks
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access measurements" ON measurements_mediapipe
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access recommendations" ON size_recommendations
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access normalized measurements" ON normalized_measurements
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_measurement_sessions_updated_at
    BEFORE UPDATE ON measurement_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE measurement_sessions IS 'Tracks measurement sessions with accuracy estimates and calibration flags';
COMMENT ON TABLE measurement_photos IS 'Stores raw photos for provenance and future model training';
COMMENT ON TABLE mediapipe_landmarks IS 'Stores MediaPipe Pose landmarks for measurement calculation';
COMMENT ON TABLE measurements_mediapipe IS 'Stores calculated measurements from MediaPipe landmarks';
COMMENT ON TABLE measurements_vendor IS 'Stores vendor API measurements for calibration only (excluded from live)';
COMMENT ON TABLE size_recommendations IS 'Stores size recommendations generated from measurements';

-- Normalized measurement payloads (JSON envelope used by MediaPipe pipeline)
CREATE TABLE normalized_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES measurement_sessions(session_id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    source TEXT DEFAULT 'mediapipe',
    model_version TEXT DEFAULT 'v1.0-mediapipe',
    confidence NUMERIC,
    accuracy_estimate NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_normalized_measurements_session ON normalized_measurements(session_id);

COMMENT ON TABLE normalized_measurements IS 'Stores normalized measurement outputs with confidence and provenance metadata';

