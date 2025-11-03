"""Measurement tools for CrewAI agents.

The legacy synopsis is preserved below so future Manus merges remain low-noise.
"""

from __future__ import annotations

LEGACY_NOTES = """
Measurement tools for CrewAI agents.

This module implements the two tools with timeout, retry, and circuit breaker
logic as recommended by ChatGPT for robust agent-backend integration.
"""

import os
import time
from typing import Dict

import requests

try:  # crewai is optional in some environments
    from crewai import tool  # type: ignore
except ImportError:  # pragma: no cover - fallback decorator

    def tool(_name: str):  # type: ignore
        def decorator(func):
            return func

        return decorator


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("X_API_KEY", "staging-secret-key")
TIMEOUT = 10  # seconds
MAX_RETRIES = 1


class CircuitBreaker:
    """Minimal circuit breaker to avoid thrashing downstream services."""

    def __init__(self, failure_threshold: int = 3) -> None:
        self.failure_threshold = failure_threshold
        self.failure_count = 0
        self.is_open = False

    def call_failed(self) -> None:
        """Record a failure and open the circuit when threshold is reached."""

        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True

    def call_succeeded(self) -> None:
        """Reset counters after a successful call."""

        self.failure_count = 0
        self.is_open = False

    def can_proceed(self) -> bool:
        """Allow further calls only when the circuit is closed."""

        return not self.is_open


validate_breaker = CircuitBreaker()
recommend_breaker = CircuitBreaker()


def _post_with_retry(url: str, payload: Dict, breaker: CircuitBreaker) -> requests.Response:
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)

            if response.status_code in {500, 502, 503, 504} and attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue

            if response.status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(5)
                continue

            return response
        except requests.exceptions.Timeout as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            raise
        except requests.exceptions.RequestException as exc:
            last_error = exc
            raise

    if last_error:
        raise last_error
    raise RuntimeError("Retry loop exited unexpectedly")


@tool("validate_measurements")
def validate_measurements(measurement_data: Dict) -> Dict:
    """Validate and normalize measurement data via the backend API."""

    if not validate_breaker.can_proceed():
        return {
            "error": "Circuit breaker is open. Too many recent failures.",
            "type": "circuit_breaker_error",
        }

    url = f"{API_BASE_URL}/measurements/validate"

    try:
        response = _post_with_retry(url, measurement_data, validate_breaker)
    except requests.exceptions.Timeout:
        validate_breaker.call_failed()
        return {"error": "Request timed out", "type": "timeout_error"}
    except requests.exceptions.RequestException as exc:
        validate_breaker.call_failed()
        return {"error": f"Request failed: {exc}", "type": "connection_error"}

    if response.status_code == 200:
        validate_breaker.call_succeeded()
        return response.json()

    if response.status_code == 422:
        validate_breaker.call_succeeded()
        return {"error": response.json().get("detail", {}), "status_code": 422}

    if response.status_code in {500, 502, 503, 504}:
        validate_breaker.call_failed()
        return {
            "error": f"Server error after {MAX_RETRIES + 1} attempts",
            "status_code": response.status_code,
            "type": "server_error",
        }

    if response.status_code == 429:
        return {
            "error": "Rate limit exceeded",
            "status_code": 429,
            "type": "rate_limit_error",
        }

    validate_breaker.call_failed()
    return {
        "error": f"Unexpected status code: {response.status_code}",
        "status_code": response.status_code,
        "type": "unexpected_error",
    }


@tool("recommend_sizes")
def recommend_sizes(normalized_measurements: Dict) -> Dict:
    """Generate size recommendations from normalized measurements."""

    if not recommend_breaker.can_proceed():
        return {
            "error": "Circuit breaker is open. Too many recent failures.",
            "type": "circuit_breaker_error",
        }

    url = f"{API_BASE_URL}/measurements/recommend"

    try:
        response = _post_with_retry(url, normalized_measurements, recommend_breaker)
    except requests.exceptions.Timeout:
        recommend_breaker.call_failed()
        return {"error": "Request timed out", "type": "timeout_error"}
    except requests.exceptions.RequestException as exc:
        recommend_breaker.call_failed()
        return {"error": f"Request failed: {exc}", "type": "connection_error"}

    if response.status_code == 200:
        recommend_breaker.call_succeeded()
        return response.json()

    if response.status_code in {500, 502, 503, 504}:
        recommend_breaker.call_failed()
        return {
            "error": f"Server error after {MAX_RETRIES + 1} attempts",
            "status_code": response.status_code,
            "type": "server_error",
        }

    if response.status_code == 429:
        return {
            "error": "Rate limit exceeded",
            "status_code": 429,
            "type": "rate_limit_error",
        }

    recommend_breaker.call_failed()
    return {
        "error": f"Unexpected status code: {response.status_code}",
        "status_code": response.status_code,
        "type": "unexpected_error",
    }

