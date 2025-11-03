"""Agent tool tests with mocked API responses.

The legacy synopsis is preserved below to keep future Manus merges low-noise.
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests


LEGACY_NOTES = """
Agent tool tests with mocked API responses.

This module tests the agent tools (validate_measurements, recommend_sizes)
with mocked backend responses to verify retry logic, circuit breaker, and error handling.
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from agents.tools.measurement_tools import recommend_sizes, validate_measurements  # noqa: E402


def test_validate_measurements_success():
    """Successful validation should return normalized measurements."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "height_cm": 170.0,
            "waist_natural_cm": pytest.approx(81.28),
            "source": "mediapipe",
            "confidence": 0.95,
            "accuracy_estimate": 0.05,
        }
        mock_post.return_value = mock_response

        result = validate_measurements(
            {
                "front_landmarks": {"landmarks": [], "timestamp": "2025-10-26T15:00:00Z"},
                "side_landmarks": {"landmarks": [], "timestamp": "2025-10-26T15:00:05Z"},
            }
        )

        assert result["source"] == "mediapipe"
        assert result["confidence"] == pytest.approx(0.95)
        assert "height_cm" in result


def test_validate_measurements_422_error():
    """Validation errors should surface detail payload to the agent."""

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
    """Timeouts should be reported with the timeout_error type."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout()

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "timeout_error"
        assert mock_post.call_count == 2  # initial call + retry


def test_validate_measurements_server_error_with_retry():
    """Server errors should trigger retries and expose type server_error."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "server_error"
        assert mock_post.call_count == 2


def test_validate_measurements_rate_limit():
    """Rate limits should be surfaced without retry after the second attempt."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert result["type"] == "rate_limit_error"
        assert mock_post.call_count == 2


def test_recommend_sizes_success():
    """Successful recommendation should pass through backend payload."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "recommendations": [
                {"category": "tops", "size": "M", "confidence": 0.9},
                {"category": "bottoms", "size": "32", "confidence": 0.85},
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
        assert result["model_version"] == "v1.0-mediapipe"


def test_recommend_sizes_server_error():
    """Server errors should report server_error and retry once."""

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
        assert mock_post.call_count == 2


def test_recommend_sizes_timeout():
    """Timeouts from the recommendation endpoint should bubble up."""

    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
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

