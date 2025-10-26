# FitTwin local stub

Start API:
  uvicorn src.server.main:app --reload

Endpoints:
  GET /measurements/
  GET /dmaas/latest

Replace stub logic with vendor mapping and Supabase once wired.

Quick local verify (use project venv):

1) Activate venv

```bash
cd ~/fitwin-crewai
source .venv/bin/activate
```

2) Run tests (offline, uses TestClient)

```bash
python -m pytest -q
```

3) Optional: run the server and smoke endpoints (new terminal)

```bash
uvicorn src.server.main:app --reload
# then in another terminal:
curl -s http://127.0.0.1:8000/measurements/ | python -m json.tool
curl -s http://127.0.0.1:8000/dmaas/latest | python -m json.tool
```

4) Safe test env file (already created): `.env.test` contains VENDOR_MODE=stub and PORT=8001
