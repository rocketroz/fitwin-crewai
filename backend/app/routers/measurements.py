"""
Measurements router for validation and recommendation endpoints.

This module implements the two main DMaaS API endpoints:
- /measurements/validate: Validate and normalize measurement input
- /measurements/recommend: Generate size recommendations from normalized measurements
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from backend.app.schemas.measure_schema import MeasurementInput, MeasurementNormalized
from backend.app.schemas.errors import ErrorResponse, ErrorDetail
from backend.app.core.validation import normalize_and_validate
from typing import Optional
import os


router = APIRouter(prefix="/measurements", tags=["measurements"])

# Simple API key check (for staging)
VALID_API_KEY = os.getenv("API_KEY", "staging-secret-key")


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for authentication."""
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                type="authentication_error",
                code="invalid_key",
                message="Invalid or missing API key",
                errors=[]
            ).dict()
        )


@router.post("/validate", response_model=MeasurementNormalized, dependencies=[Depends(verify_api_key)])
def validate_measurements(input_data: MeasurementInput):
    """
    Validate and normalize measurement input.
    
    If MediaPipe landmarks are provided, calculates measurements from landmarks.
    Otherwise, uses user-provided measurements and converts to centimeters.
    
    Returns normalized measurements with confidence scores and accuracy estimates.
    
    Args:
        input_data: Measurement input with optional MediaPipe landmarks
        
    Returns:
        Normalized measurements in centimeters with metadata
        
    Raises:
        HTTPException: 422 for validation errors, 401 for auth errors, 500 for server errors
    """
    try:
        normalized = normalize_and_validate(input_data)
        
        # Check accuracy threshold
        if normalized.accuracy_estimate and normalized.accuracy_estimate > 0.03:
            # Accuracy below 97% - flag for potential vendor calibration
            # TODO: Store flag in database for CEO Agent review
            pass
        
        return normalized
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during validation",
                errors=[ErrorDetail(field="", message=str(e))],
                session_id=input_data.session_id
            ).dict()
        )


@router.post("/recommend", response_model=dict, dependencies=[Depends(verify_api_key)])
def recommend_sizes(measurements: MeasurementNormalized):
    """
    Generate size recommendations from normalized measurements.
    
    Returns recommendations with confidence scores, processed measurements,
    and model version for API consumers.
    
    Args:
        measurements: Normalized measurements in centimeters
        
    Returns:
        Dictionary with recommendations, processed measurements, and metadata
        
    Raises:
        HTTPException: 401 for auth errors, 500 for server errors
    """
    try:
        # TODO: Import and use actual fit rules
        # from backend.app.services.fit_rules_tops import recommend_top
        # from backend.app.services.fit_rules_bottoms import recommend_bottom
        # m_dict = measurements.dict()
        # recs = [recommend_top(m_dict), recommend_bottom(m_dict)]
        
        # Placeholder implementation
        recs = [
            {
                "category": "tops",
                "size": "M",
                "confidence": 0.9,
                "rationale": "Based on chest and waist measurements"
            },
            {
                "category": "bottoms",
                "size": "32",
                "confidence": 0.85,
                "rationale": "Based on waist and inseam measurements"
            }
        ]
        
        return {
            "recommendations": recs,
            "processed_measurements": measurements,
            "model_version": measurements.model_version,
            "session_id": measurements.session_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during recommendation",
                errors=[ErrorDetail(field="", message=str(e))],
                session_id=measurements.session_id
            ).dict()
        )

