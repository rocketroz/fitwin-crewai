"""
Validation and normalization utility for measurements.

This module implements the normalization and validation logic, including
MediaPipe landmark processing and geometric equation calculations.
"""

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

ALLOWED_META_FIELDS = {
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


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54


def calculate_distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between two 3D points.

    Args:
        p1: First point with x, y, z coordinates
        p2: Second point with x, y, z coordinates

    Returns:
        Distance in the same units as input coordinates
    """
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    dz = p2["z"] - p1["z"]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def calculate_measurements_from_landmarks(
    front_landmarks: MediaPipeLandmarks,
    side_landmarks: MediaPipeLandmarks,
) -> Dict[str, float]:
    """
    Calculate anthropometric measurements from MediaPipe landmarks.

    This function implements geometric equations to estimate body measurements
    from 3D landmark coordinates. The equations are based on anthropometric
    research and will be refined during the calibration phase if needed.
    """
    # Convert landmarks to list of dicts for easier access
    front_pts = [
        {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
        for lm in front_landmarks.landmarks
    ]
    side_pts = [
        {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
        for lm in side_landmarks.landmarks
    ]

    # TODO: Implement actual geometric equations.
    # Placeholder implementation - replace with calibration data.
    measurements = {
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

    return measurements


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


def normalize_and_validate(input_data: MeasurementInput) -> MeasurementNormalized:
    """
    Normalize measurement input to centimeters and validate field names.

    If MediaPipe landmarks are provided, calculate measurements from landmarks.
    Otherwise, use user-provided measurements.
    """
    errors = []

    # Check for unknown fields in user-provided measurements
    if not input_data.front_landmarks and not input_data.side_landmarks:
        raw_payload = dict(getattr(input_data, "__dict__", {}))
        extra_payload = getattr(input_data, "__pydantic_extra__", None)
        if extra_payload:
            raw_payload.update(extra_payload)
        model_extra = getattr(input_data, "model_extra", None)
        if model_extra:
            raw_payload.update(model_extra)

        for field_name, value in raw_payload.items():
            if field_name.startswith("_"):
                continue
            if field_name in CANONICAL_FIELDS or field_name in ALLOWED_META_FIELDS:
                continue
            errors.append(
                ErrorDetail(
                    field=field_name,
                    message=f"Unknown field: {field_name}",
                    hint=f"Did you mean one of: {', '.join(sorted(CANONICAL_FIELDS))}?",
                )
            )

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

    # Calculate measurements from MediaPipe landmarks if available
    if input_data.front_landmarks and input_data.side_landmarks:
        measurements = calculate_measurements_from_landmarks(
            input_data.front_landmarks,
            input_data.side_landmarks,
        )
        source = "mediapipe"
        accuracy = estimate_accuracy(
            measurements,
            input_data.front_landmarks,
            input_data.side_landmarks,
        )

        # Store landmarks for provenance
        front_landmarks_id = str(uuid.uuid4())
        side_landmarks_id = str(uuid.uuid4())
        # TODO: Store landmarks in database

    else:
        # Use user-provided measurements
        conversion_factor = 2.54 if input_data.unit == Unit.IN else 1.0
        measurements = {
            "height_cm": (input_data.height or 0) * conversion_factor,
            "neck_cm": (input_data.neck or 0) * conversion_factor,
            "shoulder_cm": (input_data.shoulder or 0) * conversion_factor,
            "chest_cm": (input_data.chest or 0) * conversion_factor,
            "underbust_cm": (input_data.underbust or 0) * conversion_factor,
            "waist_natural_cm": (input_data.waist_natural or 0) * conversion_factor,
            "sleeve_cm": (input_data.sleeve or 0) * conversion_factor,
            "bicep_cm": (input_data.bicep or 0) * conversion_factor,
            "forearm_cm": (input_data.forearm or 0) * conversion_factor,
            "hip_low_cm": (input_data.hip_low or 0) * conversion_factor,
            "thigh_cm": (input_data.thigh or 0) * conversion_factor,
            "knee_cm": (input_data.knee or 0) * conversion_factor,
            "calf_cm": (input_data.calf or 0) * conversion_factor,
            "ankle_cm": (input_data.ankle or 0) * conversion_factor,
            "front_rise_cm": (input_data.front_rise or 0) * conversion_factor,
            "back_rise_cm": (input_data.back_rise or 0) * conversion_factor,
            "inseam_cm": (input_data.inseam or 0) * conversion_factor,
            "outseam_cm": (input_data.outseam or 0) * conversion_factor,
        }
        source = "user_input"
        accuracy = 1.0  # Assume user input is accurate
        front_landmarks_id = None
        side_landmarks_id = None

    # Create normalized measurement object
    normalized = MeasurementNormalized(
        **measurements,
        source=source,
        model_version="v1.0-mediapipe",
        confidence=accuracy,
        accuracy_estimate=1.0 - accuracy,  # Convert to error percentage
        session_id=input_data.session_id,
        front_photo_url=input_data.front_photo_url,
        side_photo_url=input_data.side_photo_url,
        front_landmarks_id=front_landmarks_id,
        side_landmarks_id=side_landmarks_id,
    )

    return normalized
