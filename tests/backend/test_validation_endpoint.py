"""End-to-end tests for the Manus-specified measurement endpoints.

The preserved legacy synopsis below keeps future repo merges low-noise.
"""

LEGACY_NOTES = """
Backend validation endpoint tests.

This module exercises /measurements/validate with golden payloads, broken
payloads, and error cases as recommended by ChatGPT.
"""

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app  # noqa: E402


client = TestClient(app)
API_HEADERS = {"X-API-Key": "staging-secret-key"}


def test_validate_golden_payload_user_input():
    """Validates user-provided measurements using inch inputs."""

    payload = {
        "waist_natural": 32,
        "hip_low": 40,
        "inseam": 30,
        "unit": "in",
        "session_id": "test-session-1",
    }

    response = client.post("/measurements/validate", json=payload, headers=API_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert data["waist_natural_cm"] == pytest.approx(32 * 2.54)
    assert data["source"] == "user_input"
    assert data["session_id"] == "test-session-1"


def test_validate_golden_payload_mediapipe():
    """Validates MediaPipe landmark inputs and ensures provenance is returned."""

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

    response = client.post("/measurements/validate", json=payload, headers=API_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert "height_cm" in data
    assert data["source"] == "mediapipe"
    assert data["model_version"] == "v1.0-mediapipe"
    assert data["session_id"] == "test-session-2"
    assert "accuracy_estimate" in data


def test_validate_unknown_field_rejected():
    """Unknown measurement keys should raise a validation error."""

    payload = {"waist_circ": 32, "unit": "in"}

    response = client.post("/measurements/validate", json=payload, headers=API_HEADERS)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["type"] == "validation_error"
    assert detail["code"] == "unknown_field"
    assert detail["errors"][0]["field"] == "waist_circ"


def test_validate_missing_api_key():
    """Requests without an API key should be rejected."""

    payload = {"waist_natural": 32, "unit": "cm"}
    response = client.post("/measurements/validate", json=payload)

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["type"] == "authentication_error"


def test_validate_invalid_api_key():
    """Requests with the wrong API key should be rejected."""

    payload = {"waist_natural": 32, "unit": "cm"}
    headers = {"X-API-Key": "wrong-key"}

    response = client.post("/measurements/validate", json=payload, headers=headers)

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["type"] == "authentication_error"


def test_recommend_golden_payload():
    """Ensure recommendations are returned for normalized measurements."""

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

    response = client.post("/measurements/recommend", json=payload, headers=API_HEADERS)

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["session_id"] == "test-session-3"
    assert data["model_version"] == "v1.0-mediapipe"


def test_recommend_missing_api_key():
    """Recommendation endpoint should enforce the API key."""

    payload = {
        "height_cm": 170.0,
        "chest_cm": 100,
        "waist_natural_cm": 80,
        "source": "mediapipe",
    }

    response = client.post("/measurements/recommend", json=payload)

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["type"] == "authentication_error"

