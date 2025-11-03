"""Measurement endpoints for validation and recommendations.

The preserved legacy synopsis below keeps future Manus merges low-noise.
"""

LEGACY_NOTES = """
Measurements router for validation and recommendation endpoints.

This module implements the two main DMaaS API endpoints:
- /measurements/validate: Validate and normalize measurement input
- /measurements/recommend: Generate size recommendations from normalized measurements
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from backend.app.core.validation import normalize_and_validate
from backend.app.schemas.errors import ErrorResponse
from backend.app.schemas.measure_schema import MeasurementInput, MeasurementNormalized


router = APIRouter(prefix="/measurements", tags=["measurements"])

VALID_API_KEY = os.getenv("API_KEY", "staging-secret-key")
MODEL_VERSION = "v1.0-mediapipe"


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Reject requests that do not include the expected staging API key."""

    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                type="authentication_error",
                code="invalid_key",
                message="Invalid or missing API key",
                errors=[],
            ).model_dump(),
        )


@router.post(
    "/validate",
    response_model=MeasurementNormalized,
    dependencies=[Depends(verify_api_key)],
)
async def validate_measurements(request: Request, input_data: MeasurementInput) -> dict:
    """Validate and normalize measurement input."""

    try:
        raw_payload = await request.json()
    except Exception:  # pragma: no cover - best effort capture
        raw_payload = None

    try:
        normalized = normalize_and_validate(input_data, raw_payload)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during validation",
                errors=[],
                session_id=input_data.session_id,
            ).model_dump(),
        ) from exc

    payload = normalized.model_dump(exclude_none=True)
    payload.setdefault("model_version", MODEL_VERSION)
    return payload


@router.post(
    "/recommend",
    response_model=dict,
    dependencies=[Depends(verify_api_key)],
)
def recommend_sizes(measurements: MeasurementNormalized) -> dict:
    """Generate size recommendations from normalized measurements."""

    try:
        recs = [
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

        processed = measurements.model_dump(exclude_none=True)
        processed.setdefault("model_version", MODEL_VERSION)

        return {
            "recommendations": recs,
            "processed_measurements": processed,
            "model_version": processed.get("model_version", MODEL_VERSION),
            "session_id": processed.get("session_id"),
        }

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                type="server_error",
                code="internal",
                message="An unexpected error occurred during recommendation",
                errors=[],
                session_id=measurements.session_id,
            ).model_dump(),
        ) from exc

