# FitTwin (local stub)

Two-photo measurement mapping for upper and lower body with safe, offline tests. The API returns a normalized body measurement schema and simple recommendations for tops and bottoms. The code runs locally and does not call external vendors by default.

## Quick start

```bash
# 1) clone or open the repo, then:
cd ~/fitwin-crewai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if you have one; otherwise install fastapi uvicorn pytest
# pip install fastapi uvicorn pytest

# 2) run tests (offline via FastAPI TestClient)
python -m pytest -q

# 3) start the API
uvicorn src.server.main:app --reload
# open http://127.0.0.1:8000/docs
```

Example requests

```bash
curl -s http://127.0.0.1:8000/measurements/ | python -m json.tool
curl -s http://127.0.0.1:8000/dmaas/latest | python -m json.tool
```

Sample response: /measurements/

```json
{
  "status": "success",
  "data": {
    "neck_cm": 35.0,
    "shoulder_cm": 44.0,
    "chest_cm": 96.0,
    "underbust_cm": 84.0,
    "waist_natural_cm": 82.5,
    "sleeve_cm": 61.0,
    "bicep_cm": 31.0,
    "forearm_cm": 26.0,
    "hip_low_cm": 98.0,
    "thigh_cm": 56.0,
    "knee_cm": 39.0,
    "calf_cm": 36.0,
    "ankle_cm": 23.0,
    "front_rise_cm": 27.5,
    "back_rise_cm": 36.0,
    "inseam_cm": 76.0,
    "outseam_cm": 100.0,
    "source": "vendor",
    "vendor_version": "stub-2photo",
    "confidence": 0.92
  }
}
```

Sample response: /dmaas/latest

```json
{
  "measurement": { "...": "see schema above" },
  "recommendations": [
    { "category": "top", "size": "M", "confidence": 0.7, "rationale": "chest, shoulder, sleeve" },
    { "category": "bottom", "size": "32x30", "confidence": 0.72, "rationale": "waist and inseam" }
  ]
}
```

## Environment

The app reads simple settings from the environment.

- ENV default dev
- VENDOR_MODE stub or real (default stub)
- PORT default 8000

Use .env.test for tests and .env.dev for local runs. Example file is in .env.example.

# stub mode (default)
VENDOR_MODE=stub uvicorn src.server.main:app --reload

# real mode placeholder
VENDOR_MODE=real uvicorn src.server.main:app --reload

## Project layout

```
src/
  server/
    api/
      dmaas.py
      measurement_job.py
    fit_rules_bottoms.py
    fit_rules_tops.py
    measure_schema.py
    models.py
    normalize.py
    settings.py
    vendor_client.py
tests/
  test_measure_and_recs.py
.vscode/
  launch.json
```

## Where to extend

- Vendor integration: implement fetch_real_vendor in `vendor_client.py` and keep VENDOR_MODE switch.
- Normalization: add mappers in `normalize.py` if a vendor introduces new fields.
- Fit rules: replace placeholder logic in `fit_rules_tops.py` and `fit_rules_bottoms.py` with size charts and ease variants, plus unit tests.

## Roll back

This repo is tagged at baseline/v1.0.

```
git checkout baseline/v1.0
```

## Badges (placeholders)

Add CI / coverage badges here once configured.
