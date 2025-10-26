from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_measurements_full_schema():
    r = client.get("/measurements/")
    assert r.status_code == 200
    d = r.json()["data"]
    for k in ["neck_cm","shoulder_cm","chest_cm","waist_natural_cm","hip_low_cm","inseam_cm"]:
        assert k in d


def test_dmaas_both_categories():
    r = client.get("/dmaas/latest")
    assert r.status_code == 200
    payload = r.json()
    recs = payload["recommendations"]
    cats = {r["category"] for r in recs}
    assert "top" in cats and "bottom" in cats
