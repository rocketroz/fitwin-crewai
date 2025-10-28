from fastapi.testclient import TestClient
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `backend` can be imported
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from backend.app.main import app


client = TestClient(app)
headers = {"X-API-Key": "staging-secret-key"}

validation_payload = {
    "waist_natural": 32,
    "hip_low": 40,
    "inseam": 30,
    "unit": "in",
    "session_id": "demo-cli",
}

validation_response = client.post(
    "/measurements/validate", json=validation_payload, headers=headers
)
print(json.dumps(validation_response.json(), indent=2))

recommend_payload = {
    **validation_response.json(),
    "session_id": "demo-cli",
}

recommend_response = client.post(
    "/measurements/recommend", json=recommend_payload, headers=headers
)
print("---")
print(json.dumps(recommend_response.json(), indent=2))
