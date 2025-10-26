from fastapi.testclient import TestClient
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `backend` can be imported
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from backend.app.main import app

c = TestClient(app)
print(json.dumps(c.get('/measurements/').json(), indent=2))
print('---')
print(json.dumps(c.get('/dmaas/latest').json(), indent=2))
