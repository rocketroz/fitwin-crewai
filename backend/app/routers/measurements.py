"""
Measurement endpoints for validation and recommendations.

These endpoints provide the DMaaS functionality described in the Manus package:
- POST /measurements/validate
- POST /measurements/recommend
"""

from typing import Optional
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backend.app.schemas.errors import ErrorDetail, ErrorResponse
from backend.app.schemas.measure_schema import MeasurementInput, MeasurementNormalized
from backend.app.core.validation import normalize_and_validate


router = APIRouter(prefix="/measurements", tags=["measurements"])

# Simple API key gate for staging environments.
VALID_API_KEY = os.getenv("API_KEY", "staging-secret-key")


def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Fail requests that do not provide the expected staging API key."""
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                type="authentication_error",
                code="invalid_key",
                message="Invalid or missing API key",
                errors=[],
            ).dict(),
        )


@router.post(
    "/validate",
    response_model=MeasurementNormalized,
    dependencies=[Depends(verify_api_key)],
)
async def validate_measurements(request: Request, input_data: MeasurementInput):
    """
    Validate and normalize measurement input.

    MediaPipe landmarks, when provided, are converted into anthropometric
    measurements. Otherwise raw user measurements are normalized to centimeters.
    """
    try:
        raw_payload = await request.json()
        normalized = normalize_and_validate(input_data, raw_payload)

        # Placeholder accuracy flag for CEO review.
        if normalized.accuracy_estimate and normalized.accuracy_estimate > 0.03:
            # TODO: persist flag for later review/escalation.
            pass

        return normalized

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during validation",
                errors=[ErrorDetail(field="", message=str(exc))],
                session_id=input_data.session_id,
            ).dict(),
        ) from exc


@router.post(
    "/recommend",
    response_model=dict,
    dependencies=[Depends(verify_api_key)],
)
def recommend_sizes(measurements: MeasurementNormalized):
    """
    Generate size recommendations from normalized measurements.

    Actual fit rule integration is pending; we return a stubbed payload for now.
    """
    try:
        # TODO: replace placeholders with calls into fit rule services.
        recommendations = [
            {
                "category": "tops",
                "size": "M",
                "confidence": 0.9,
                "rationale": "Based on chest and waist measurements",
            },
            {
                "category": "bottoms",
                "size": "32",
                "confidence": 0.85,
                "rationale": "Based on waist and inseam measurements",
            },
        ]

        return {
            "recommendations": recommendations,
            "processed_measurements": measurements,
            "model_version": measurements.model_version,
            "session_id": measurements.session_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during recommendation",
                errors=[ErrorDetail(field="", message=str(exc))],
                session_id=measurements.session_id,
            ).dict(),
        ) from exc
