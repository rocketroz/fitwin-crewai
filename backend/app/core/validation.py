"""
Normalization and validation utilities for measurement payloads.

Implements heuristics for MediaPipe landmark processing and unit conversion.
Derived from the Manus implementation package.
"""

from __future__ import annotations

import math
import uuid
from typing import Dict

from fastapi import HTTPException

from backend.app.schemas.errors import ErrorDetail, ErrorResponse
from backend.app.schemas.measure_schema import (
    MeasurementInput,
    MeasurementNormalized,
    MediaPipeLandmarks,
    Unit,
)


CANONICAL_FIELDS = {
    "height",
    "neck",
    "shoulder",
    "chest",
    "underbust",
    "waist_natural",
    "sleeve",
    "bicep",
    "forearm",
    "hip_low",
    "thigh",
    "knee",
    "calf",
    "ankle",
    "front_rise",
    "back_rise",
    "inseam",
    "outseam",
}


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54


def calculate_distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    """Calculate Euclidean distance between two 3D points."""
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    dz = p2["z"] - p1["z"]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def calculate_measurements_from_landmarks(
    front_landmarks: MediaPipeLandmarks,
    side_landmarks: MediaPipeLandmarks,
) -> Dict[str, float]:
    """
    Derive anthropometric measurements from MediaPipe landmarks.

    Placeholder implementation until calibrated formulas are available.
    """
    # TODO: Replace placeholder logic with geometric equations.
    return {
        "height_cm": 170.0,
        "neck_cm": 38.0,
        "shoulder_cm": 45.0,
        "chest_cm": 100.0,
        "underbust_cm": 85.0,
        "waist_natural_cm": 80.0,
        "sleeve_cm": 60.0,
        "bicep_cm": 30.0,
        "forearm_cm": 25.0,
        "hip_low_cm": 100.0,
        "thigh_cm": 55.0,
        "knee_cm": 38.0,
        "calf_cm": 35.0,
        "ankle_cm": 22.0,
        "front_rise_cm": 25.0,
        "back_rise_cm": 35.0,
        "inseam_cm": 76.0,
        "outseam_cm": 100.0,
    }


def estimate_accuracy(
    measurements: Dict[str, float],
    front_landmarks: MediaPipeLandmarks,
    side_landmarks: MediaPipeLandmarks,
) -> float:
    """
    Estimate accuracy of MediaPipe-derived measurements (0-1 scale).

    Uses visibility heuristics as a stand-in until calibration data is available.
    """
    front_scores = [lm.visibility for lm in front_landmarks.landmarks]
    side_scores = [lm.visibility for lm in side_landmarks.landmarks]
    avg_visibility = (sum(front_scores) + sum(side_scores)) / (
        len(front_scores) + len(side_scores)
    )

    if avg_visibility > 0.8:
        return 0.95
    if avg_visibility > 0.6:
        return 0.9
    return 0.85


def _unknown_field_errors(input_data: MeasurementInput, raw_payload: Dict | None = None):
    allowed = CANONICAL_FIELDS | {
        "unit",
        "session_id",
        "front_landmarks",
        "side_landmarks",
        "front_photo_url",
        "side_photo_url",
        "source_type",
        "platform",
        "arkit_body_anchor",
        "arkit_depth_map",
        "browser_info",
        "processing_location",
        "device_id",
    }

    if raw_payload is None:
        input_dict = (
            input_data.model_dump(exclude_unset=True)
            if hasattr(input_data, "model_dump")
            else input_data.dict(exclude_unset=True)
        )
        keys = set(input_dict.keys())
    else:
        keys = set(raw_payload.keys())

    for field_name in keys:
        if field_name not in allowed:
            yield ErrorDetail(
                field=field_name,
                message=f"Unknown field: {field_name}",
                hint=f"Did you mean one of: {', '.join(sorted(CANONICAL_FIELDS))}?",
            )


def normalize_and_validate(
    input_data: MeasurementInput, raw_payload: Dict | None = None
) -> MeasurementNormalized:
    """Normalize incoming measurement payloads and validate canonical fields."""
    errors = list(_unknown_field_errors(input_data, raw_payload))
    if errors:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                type="validation_error",
                code="unknown_field",
                message="One or more fields are not recognized",
                errors=errors,
                session_id=input_data.session_id,
            ).dict(),
        )

    if input_data.front_landmarks and input_data.side_landmarks:
        measurements = calculate_measurements_from_landmarks(
            input_data.front_landmarks, input_data.side_landmarks
        )
        source = "mediapipe"
        accuracy = estimate_accuracy(
            measurements, input_data.front_landmarks, input_data.side_landmarks
        )
        front_landmarks_id = str(uuid.uuid4())
        side_landmarks_id = str(uuid.uuid4())
        # TODO: persist landmarks for provenance.
    else:
        conversion = 2.54 if input_data.unit == Unit.IN else 1.0
        measurements = {
            "height_cm": (input_data.height or 0) * conversion,
            "neck_cm": (input_data.neck or 0) * conversion,
            "shoulder_cm": (input_data.shoulder or 0) * conversion,
            "chest_cm": (input_data.chest or 0) * conversion,
            "underbust_cm": (input_data.underbust or 0) * conversion,
            "waist_natural_cm": (input_data.waist_natural or 0) * conversion,
            "sleeve_cm": (input_data.sleeve or 0) * conversion,
            "bicep_cm": (input_data.bicep or 0) * conversion,
            "forearm_cm": (input_data.forearm or 0) * conversion,
            "hip_low_cm": (input_data.hip_low or 0) * conversion,
            "thigh_cm": (input_data.thigh or 0) * conversion,
            "knee_cm": (input_data.knee or 0) * conversion,
            "calf_cm": (input_data.calf or 0) * conversion,
            "ankle_cm": (input_data.ankle or 0) * conversion,
            "front_rise_cm": (input_data.front_rise or 0) * conversion,
            "back_rise_cm": (input_data.back_rise or 0) * conversion,
            "inseam_cm": (input_data.inseam or 0) * conversion,
            "outseam_cm": (input_data.outseam or 0) * conversion,
        }
        source = "user_input"
        accuracy = 1.0
        front_landmarks_id = None
        side_landmarks_id = None

    return MeasurementNormalized(
        **measurements,
        source=source,
        model_version="v1.0-mediapipe",
        confidence=accuracy,
        accuracy_estimate=1.0 - accuracy,
        session_id=input_data.session_id,
        front_photo_url=input_data.front_photo_url,
        side_photo_url=input_data.side_photo_url,
        front_landmarks_id=front_landmarks_id,
        side_landmarks_id=side_landmarks_id,
    )
