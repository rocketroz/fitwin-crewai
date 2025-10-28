"""
Unit tests for the Manus measurement agent tools.
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

# Ensure local project imports resolve.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.tools.measurement_tools import recommend_sizes, validate_measurements  # noqa: E402


def test_validate_measurements_success():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "height_cm": 170.0,
            "waist_natural_cm": 81.28,
            "source": "mediapipe",
            "confidence": 0.95,
            "accuracy_estimate": 0.05,
        }
        mock_post.return_value = mock_response

        result = validate_measurements(
            {
                "front_landmarks": {
                    "landmarks": [],
                    "timestamp": "2025-10-26T15:00:00Z",
                },
                "side_landmarks": {
                    "landmarks": [],
                    "timestamp": "2025-10-26T15:00:05Z",
                },
            }
        )

        assert result["source"] == "mediapipe"
        assert result["confidence"] == 0.95


def test_validate_measurements_422_error():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": {
                "type": "validation_error",
                "code": "unknown_field",
                "message": "Unknown field",
                "errors": [
                    {
                        "field": "waist_circ",
                        "message": "Unknown field",
                        "hint": "Did you mean waist_natural?",
                    }
                ],
            }
        }
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_circ": 32, "unit": "in"})

        assert result["status_code"] == 422
        assert "waist_circ" in str(result["error"])


def test_validate_measurements_timeout():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "timeout_error"
        assert mock_post.call_count == 2


def test_validate_measurements_server_error_with_retry():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "server_error"
        assert mock_post.call_count == 2


def test_validate_measurements_rate_limit():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "rate_limit_error"
        assert mock_post.call_count == 2


def test_recommend_sizes_success():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recommendations": [
                {
                    "category": "tops",
                    "size": "M",
                    "confidence": 0.9,
                    "rationale": "Based on chest and waist",
                },
                {
                    "category": "bottoms",
                    "size": "32",
                    "confidence": 0.85,
                    "rationale": "Based on waist and inseam",
                },
            ],
            "model_version": "v1.0-mediapipe",
            "session_id": "test-123",
        }
        mock_post.return_value = mock_response

        result = recommend_sizes(
            {
                "height_cm": 170.0,
                "chest_cm": 100,
                "waist_natural_cm": 80,
                "source": "mediapipe",
            }
        )

        assert len(result["recommendations"]) == 2
        assert result["recommendations"][0]["category"] == "tops"


def test_recommend_sizes_server_error():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = recommend_sizes(
            {
                "height_cm": 170.0,
                "chest_cm": 100,
                "waist_natural_cm": 80,
                "source": "mediapipe",
            }
        )

        assert result["type"] == "server_error"


def test_recommend_sizes_timeout():
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        result = recommend_sizes(
            {
                "height_cm": 170.0,
                "chest_cm": 100,
                "waist_natural_cm": 80,
                "source": "mediapipe",
            }
        )

        assert result["type"] == "timeout_error"
        assert mock_post.call_count == 2
