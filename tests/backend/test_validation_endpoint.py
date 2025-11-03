"""
Backend validation endpoint tests.

This module tests the /measurements/validate endpoint with golden payloads,
broken payloads, and error cases as recommended by ChatGPT.
"""

from pathlib import Path
import sys

from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from backend.app.main import app

client = TestClient(app)


def test_validate_golden_payload_user_input():
    """Test with a valid user-provided payload - should return normalized measurements."""
    payload = {
        "waist_natural": 32,
        "hip_low": 40,
        "inseam": 30,
        "unit": "in",
        "session_id": "test-session-1",
    }
    headers = {"X-API-Key": "staging-secret-key"}

    response = client.post("/measurements/validate", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "waist_natural_cm" in data
    assert data["waist_natural_cm"] == 32 * 2.54  # Converted to cm
    assert data["source"] == "user_input"
    assert data["session_id"] == "test-session-1"


def test_validate_golden_payload_mediapipe():
    """Test with valid MediaPipe landmarks - should return calculated measurements."""
    payload = {
        "front_landmarks": {
            "landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}] * 33,
            "timestamp": "2025-10-26T15:00:00Z",
            "image_width": 1920,
            "image_height": 1080,
        },
        "side_landmarks": {
            "landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9}] * 33,
            "timestamp": "2025-10-26T15:00:05Z",
            "image_width": 1920,
            "image_height": 1080,
        },
        "front_photo_url": "https://storage.fittwin.com/photos/test/front.jpg",
        "side_photo_url": "https://storage.fittwin.com/photos/test/side.jpg",
        "session_id": "test-session-2",
    }
    headers = {"X-API-Key": "staging-secret-key"}

    response = client.post("/measurements/validate", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "height_cm" in data
    assert data["source"] == "mediapipe"
    assert data["model_version"] == "v1.0-mediapipe"
    assert data["session_id"] == "test-session-2"
    assert "accuracy_estimate" in data


def test_validate_broken_payload():
    """Test with an invalid payload - should return 422 with error details."""
    payload = {
        "waist_circ": 32,  # Wrong field name
        "unit": "in",
    }
    headers = {"X-API-Key": "staging-secret-key"}

    response = client.post("/measurements/validate", json=payload, headers=headers)

    assert response.status_code == 422
    error = response.json()["detail"]
    assert error["type"] == "validation_error"
    assert error["code"] == "unknown_field"
    assert len(error["errors"]) > 0
    assert "waist_circ" in error["errors"][0]["field"]
    assert "hint" in error["errors"][0]


def test_validate_missing_api_key():
    """Test without API key - should return 401."""
    payload = {"waist_natural": 32, "unit": "cm"}

    response = client.post("/measurements/validate", json=payload)

    assert response.status_code == 401
    error = response.json()["detail"]
    assert error["type"] == "authentication_error"


def test_validate_invalid_api_key():
    """Test with invalid API key - should return 401."""
    payload = {"waist_natural": 32, "unit": "cm"}
    headers = {"X-API-Key": "wrong-key"}

    response = client.post("/measurements/validate", json=payload, headers=headers)

    assert response.status_code == 401
    error = response.json()["detail"]
    assert error["type"] == "authentication_error"


def test_recommend_golden_payload():
    """Test recommendation with valid normalized measurements."""
    payload = {
        "height_cm": 170.0,
        "neck_cm": 40,
        "shoulder_cm": 45,
        "chest_cm": 100,
        "underbust_cm": 85,
        "waist_natural_cm": 80,
        "sleeve_cm": 60,
        "bicep_cm": 30,
        "forearm_cm": 25,
        "hip_low_cm": 100,
        "thigh_cm": 55,
        "knee_cm": 38,
        "calf_cm": 35,
        "ankle_cm": 22,
        "front_rise_cm": 25,
        "back_rise_cm": 35,
        "inseam_cm": 76,
        "outseam_cm": 100,
        "source": "mediapipe",
        "model_version": "v1.0-mediapipe",
        "confidence": 0.95,
        "session_id": "test-session-3",
    }
    headers = {"X-API-Key": "staging-secret-key"}

    response = client.post("/measurements/recommend", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "model_version" in data
    assert "session_id" in data
    assert len(data["recommendations"]) > 0
    assert data["session_id"] == "test-session-3"


def test_recommend_missing_api_key():
    """Test recommendation without API key - should return 401."""
    payload = {
        "height_cm": 170.0,
        "chest_cm": 100,
        "waist_natural_cm": 80,
        "source": "mediapipe",
    }

    response = client.post("/measurements/recommend", json=payload)

    assert response.status_code == 401
    error = response.json()["detail"]
    assert error["type"] == "authentication_error"
