"""
Measurement validation and recommendation tools for CrewAI agents.

Includes simple retry and circuit breaker logic based on the Manus package.
"""

from __future__ import annotations

import os
import time
from typing import Dict

import requests

try:  # crewai is optional for test environments
    from crewai import tool
except ImportError:  # pragma: no cover - fallback for environments without crewai
    def tool(_name: str):  # type: ignore
        def decorator(func):
            return func

        return decorator


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("X_API_KEY", "staging-secret-key")
TIMEOUT = 10
Measurement tools for CrewAI agents.

This module implements the two tools with timeout, retry, and circuit breaker
logic as recommended by ChatGPT for robust agent-backend integration.
"""

import requests
import os
import time
from crewai import tool
from typing import Optional


# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("X_API_KEY", "staging-secret-key")
TIMEOUT = 10  # seconds
MAX_RETRIES = 1


class CircuitBreaker:
    """Minimal circuit breaker to avoid thrashing downstream services."""

    def __init__(self, failure_threshold: int = 3):
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


    """Simple circuit breaker to prevent thrashing on repeated failures."""
    
    def __init__(self, failure_threshold=3):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.is_open = False
    
    def call_failed(self):
        """Record a failed call and open circuit if threshold exceeded."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
    
    def call_succeeded(self):
        """Record a successful call and reset the circuit."""
        self.failure_count = 0
        self.is_open = False
    
    def can_proceed(self):
        """Check if calls can proceed (circuit is closed)."""
        return not self.is_open


# Global circuit breakers for each endpoint
validate_breaker = CircuitBreaker()
recommend_breaker = CircuitBreaker()


def _post_with_retry(url: str, payload: Dict, breaker: CircuitBreaker) -> requests.Response:
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    last_error = None
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
    # Fallback should never execute.
    raise RuntimeError("Retry loop exited unexpectedly")


@tool("validate_measurements")
def validate_measurements(measurement_data: Dict) -> Dict:
    """
    Validate and normalize measurement data via the backend API.

    Supports both user-provided inputs and MediaPipe landmarks.
@tool("validate_measurements")
def validate_measurements(measurement_data: dict) -> dict:
    """
    Validates and normalizes measurement data via the backend API.
    
    Supports both user-provided measurements and MediaPipe landmarks.
    Returns normalized measurements in centimeters with confidence scores.
    
    Args:
        measurement_data: Dictionary with measurement fields or MediaPipe landmarks
        
    Returns:
        Dictionary with normalized measurements or error information
    """
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
    """
    Generate size recommendations from normalized measurements via the backend.
            "type": "circuit_breaker_error"
        }
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    url = f"{API_BASE_URL}/measurements/validate"
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, json=measurement_data, headers=headers, timeout=TIMEOUT)
            
            if response.status_code == 200:
                validate_breaker.call_succeeded()
                return response.json()
            
            elif response.status_code == 422:
                # Validation error - don't retry, return error details
                validate_breaker.call_succeeded()  # Not a system failure
                error_data = response.json()
                return {
                    "error": error_data.get("detail", {}),
                    "status_code": 422
                }
            
            elif response.status_code in [500, 502, 503, 504]:
                # Server error - retry once
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    validate_breaker.call_failed()
                    return {
                        "error": f"Server error after {MAX_RETRIES + 1} attempts",
                        "status_code": response.status_code,
                        "type": "server_error"
                    }
            
            elif response.status_code == 429:
                # Rate limit - retry once with backoff
                if attempt < MAX_RETRIES:
                    time.sleep(5)
                    continue
                else:
                    return {
                        "error": "Rate limit exceeded",
                        "status_code": 429,
                        "type": "rate_limit_error"
                    }
            
            else:
                # Other error
                validate_breaker.call_failed()
                return {
                    "error": f"Unexpected status code: {response.status_code}",
                    "status_code": response.status_code,
                    "type": "unexpected_error"
                }
        
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            else:
                validate_breaker.call_failed()
                return {
                    "error": "Request timed out",
                    "type": "timeout_error"
                }
        
        except requests.exceptions.RequestException as e:
            validate_breaker.call_failed()
            return {
                "error": f"Request failed: {str(e)}",
                "type": "connection_error"
            }
    
    return {"error": "Unexpected failure in retry loop", "type": "unknown_error"}


@tool("recommend_sizes")
def recommend_sizes(normalized_measurements: dict) -> dict:
    """
    Generates size recommendations from normalized measurements.
    
    Returns recommendations with confidence scores, processed measurements,
    and model version for API consumers.
    
    Args:
        normalized_measurements: Dictionary with normalized measurements in cm
        
    Returns:
        Dictionary with size recommendations or error information
    """
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
            "type": "circuit_breaker_error"
        }
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    url = f"{API_BASE_URL}/measurements/recommend"
    
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(url, json=normalized_measurements, headers=headers, timeout=TIMEOUT)
            
            if response.status_code == 200:
                recommend_breaker.call_succeeded()
                return response.json()
            
            elif response.status_code in [500, 502, 503, 504]:
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt)
                    continue
                else:
                    recommend_breaker.call_failed()
                    return {
                        "error": f"Server error after {MAX_RETRIES + 1} attempts",
                        "status_code": response.status_code,
                        "type": "server_error"
                    }
            
            elif response.status_code == 429:
                if attempt < MAX_RETRIES:
                    time.sleep(5)
                    continue
                else:
                    return {
                        "error": "Rate limit exceeded",
                        "status_code": 429,
                        "type": "rate_limit_error"
                    }
            
            else:
                recommend_breaker.call_failed()
                return {
                    "error": f"Unexpected status code: {response.status_code}",
                    "status_code": response.status_code,
                    "type": "unexpected_error"
                }
        
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                continue
            else:
                recommend_breaker.call_failed()
                return {
                    "error": "Request timed out",
                    "type": "timeout_error"
                }
        
        except requests.exceptions.RequestException as e:
            recommend_breaker.call_failed()
            return {
                "error": f"Request failed: {str(e)}",
                "type": "connection_error"
            }
    
    return {"error": "Unexpected failure in retry loop", "type": "unknown_error"}

