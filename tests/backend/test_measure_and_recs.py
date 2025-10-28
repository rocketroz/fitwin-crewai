from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "staging-secret-key"}


def test_measurements_full_schema():
    response = client.post(
        "/measurements/validate",
        json={
            "waist_natural": 32,
            "hip_low": 40,
            "inseam": 30,
            "unit": "in",
            "session_id": "pytest-validate",
        },
        headers=HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    for key in [
        "neck_cm",
        "shoulder_cm",
        "chest_cm",
        "waist_natural_cm",
        "hip_low_cm",
        "inseam_cm",
    ]:
        assert key in data


def test_recommend_both_categories():
    payload = {
        "height_cm": 170.0,
        "neck_cm": 38.0,
        "shoulder_cm": 45.0,
        "chest_cm": 100.0,
        "underbust_cm": 85.0,
        "waist_natural_cm": 80.0,
        "sleeve_cm": 60.0,
        "bicep_cm": 30.0,
        "forearm_cm": 25.0,
        "hip_low_cm": 100.0,
        "thigh_cm": 55.0,
        "knee_cm": 38.0,
        "calf_cm": 35.0,
        "ankle_cm": 22.0,
        "front_rise_cm": 25.0,
        "back_rise_cm": 35.0,
        "inseam_cm": 76.0,
        "outseam_cm": 100.0,
        "source": "mediapipe",
        "model_version": "v1.0-mediapipe",
        "confidence": 0.95,
        "session_id": "pytest-recommend",
    }

    response = client.post("/measurements/recommend", json=payload, headers=HEADERS)

    assert response.status_code == 200
    recs = response.json()["recommendations"]
    categories = {rec["category"] for rec in recs}
    assert {"tops", "bottoms"}.issubset(categories)
