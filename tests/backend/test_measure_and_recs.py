from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)
HEADERS = {"X-API-Key": "staging-secret-key"}


def test_measurements_validate_and_normalize_flow():
    """End-to-end smoke test: user payload -> normalized measurements."""
    payload = {
        "height": 68,
        "chest": 40,
        "waist_natural": 32,
        "hip_low": 39,
        "unit": "in",
        "session_id": "smoke-session",
    }

    response = client.post(
        "/measurements/validate",
        json=payload,
        headers=HEADERS,
    )

    assert response.status_code == 200
    normalized = response.json()
    assert normalized["source"] == "user_input"
    assert normalized["session_id"] == "smoke-session"
    assert normalized["waist_natural_cm"] == 32 * 2.54


def test_dmaas_recommendations_flow():
    """End-to-end smoke test: normalized payload -> recommendations."""
    payload = {
        "height_cm": 172.0,
        "neck_cm": 38.0,
        "shoulder_cm": 45.0,
        "chest_cm": 100.0,
        "underbust_cm": 85.0,
        "waist_natural_cm": 82.0,
        "sleeve_cm": 61.0,
        "bicep_cm": 31.0,
        "forearm_cm": 26.0,
        "hip_low_cm": 99.0,
        "thigh_cm": 56.0,
        "knee_cm": 39.0,
        "calf_cm": 36.0,
        "ankle_cm": 23.0,
        "front_rise_cm": 27.0,
        "back_rise_cm": 36.0,
        "inseam_cm": 76.0,
        "outseam_cm": 100.0,
        "source": "mediapipe",
        "model_version": "v1.0-mediapipe",
        "confidence": 0.95,
        "session_id": "smoke-session",
    }

    response = client.post(
        "/measurements/recommend",
        json=payload,
        headers=HEADERS,
    )

    assert response.status_code == 200
    rec_payload = response.json()
    assert rec_payload["session_id"] == "smoke-session"
    categories = {rec["category"] for rec in rec_payload["recommendations"]}
    assert categories == {"tops", "bottoms"}
