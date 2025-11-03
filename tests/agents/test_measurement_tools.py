"""
Agent tool tests with mocked API responses.

This module tests the agent tools (validate_measurements, recommend_sizes)
with mocked backend responses to verify retry logic, circuit breaker, and error handling.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from agents.tools.measurement_tools import recommend_sizes, validate_measurements


def test_validate_measurements_success():
    """Test successful validation with MediaPipe landmarks."""
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
                "front_landmarks": {"landmarks": [], "timestamp": "2025-10-26T15:00:00Z"},
                "side_landmarks": {"landmarks": [], "timestamp": "2025-10-26T15:00:05Z"},
            }
        )

        assert "height_cm" in result
        assert result["source"] == "mediapipe"
        assert result["confidence"] == 0.95


def test_validate_measurements_422_error():
    """Test validation error handling."""
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

        assert "error" in result
        assert result["status_code"] == 422
        assert "waist_circ" in str(result["error"])


def test_validate_measurements_timeout():
    """Test timeout handling with retry."""
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        import requests

        mock_post.side_effect = requests.exceptions.Timeout()

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert "error" in result
        assert result["type"] == "timeout_error"
        assert mock_post.call_count == 2  # Initial + 1 retry


def test_validate_measurements_server_error_with_retry():
    """Test server error handling with retry."""
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert "error" in result
        assert result["type"] == "server_error"
        assert mock_post.call_count == 2  # Initial + 1 retry


def test_validate_measurements_rate_limit():
    """Test rate limit handling."""
    with patch("agents.tools.measurement_tools.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        result = validate_measurements({"waist_natural": 32, "unit": "in"})

        assert "error" in result
        assert result["type"] == "rate_limit_error"
        assert mock_post.call_count == 2  # Initial + 1 retry


def test_recommend_sizes_success():
    """Test successful size recommendation."""
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

        assert "recommendations" in result
        assert len(result["recommendations"]) == 2
        assert result["recommendations"][0]["category"] == "tops"


def test_recommend_sizes_server_error():
    """Test server error handling in recommend_sizes."""
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

        assert "error" in result
        assert result["type"] == "server_error"


def test_recommend_sizes_timeout():
    """Test timeout handling in recommend_sizes."""
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

        assert "error" in result
        assert result["type"] == "timeout_error"
        assert mock_post.call_count == 2  # Initial + 1 retry
