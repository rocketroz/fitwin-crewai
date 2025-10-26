import os
import json
import textwrap

FILES = {
    "src/client/photoCaptureStub.js": textwrap.dedent("""
    // Minimal stub for two-photo capture
    export async function capturePhotos() {
      // TODO: integrate real camera flow; return two fake Blobs for now
      return { front: new Blob(['front'], {type: 'image/jpeg'}), side: new Blob(['side'], {type: 'image/jpeg'}) };
    }
    """).strip(),

    "src/server/api/measurement_job.py": textwrap.dedent("""
    from fastapi import APIRouter
    router = APIRouter(prefix="/measurements", tags=["measurements"])

    @router.get("/")
    def get_measurements():
      return {"status": "success", "data": "stub"}  # replace with vendor mapping later
    """).strip(),

    "src/server/api/dmaas.py": textwrap.dedent("""
    from fastapi import APIRouter
    router = APIRouter(prefix="/dmaas", tags=["dmaas"])

    @router.get("/latest")
    def get_latest():
      return {"measurement": "latest data", "recommendation": "exercise more"}  # stub
    """).strip(),

    "src/server/main.py": textwrap.dedent("""
    from fastapi import FastAPI
    from src.server.api.measurement_job import router as measurements
    from src.server.api.dmaas import router as dmaas

    app = FastAPI(title="FitTwin Local Stub")
    app.include_router(measurements)
    app.include_router(dmaas)
    """).strip(),

    "migrations/init_schema.sql": textwrap.dedent("""
    -- Minimal demo schema (local reference)
    create table if not exists measurements (
      id serial primary key,
      user_id text,
      data jsonb,
      created_at timestamptz default now()
    );
    """).strip(),

    "migrations/init_rls.sql": textwrap.dedent("""
    -- Placeholder RLS notes. Apply real policies in Supabase project.
    -- alter table measurements enable row level security;
    """).strip(),

    "README_LOCAL.md": textwrap.dedent("""
    # FitTwin local stub

    Start API:
      uvicorn src.server.main:app --reload

    Endpoints:
      GET /measurements/
      GET /dmaas/latest

    Replace stub logic with vendor mapping and Supabase once wired.
    """).strip()
}

def write_files():
    created = []
    for path, content in FILES.items():
        dirpath = os.path.dirname(path) or "."
        os.makedirs(dirpath, exist_ok=True)
        with open(path, "w") as f:
            f.write(content + "\n")
        created.append(path)
    return created

if __name__ == "__main__":
    files = write_files()
    print(json.dumps({"created": files}, indent=2))
