"""
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

