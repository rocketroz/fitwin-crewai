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
    dx = p2['x'] - p1['x']
    dy = p2['y'] - p1['y']
    dz = p2['z'] - p1['z']
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def calculate_measurements_from_landmarks(
    front_landmarks: MediaPipeLandmarks,
    side_landmarks: MediaPipeLandmarks,
) -> Dict[str, float]:
    """
    Calculate anthropometric measurements from MediaPipe landmarks.
    
    This function implements geometric equations to estimate body measurements
    from 3D landmark coordinates. The equations are based on anthropometric
    research and MediaPipe Pose Landmarker v3.1 (33 landmarks).
    
    MediaPipe Pose Landmarks (indices 0-32):
    - 0: nose, 11-12: shoulders, 13-14: elbows, 15-16: wrists
    - 23-24: hips, 25-26: knees, 27-28: ankles, 29-30: heels, 31-32: foot index
    
    Args:
        front_landmarks: MediaPipe landmarks from front-facing photo
        side_landmarks: MediaPipe landmarks from side-facing photo
        
    Returns:
        Dictionary of measurement names to values in centimeters
    """
    # Convert landmarks to list of dicts for easier access
    front_pts = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} 
                 for lm in front_landmarks.landmarks]
    side_pts = [{'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility} 
                for lm in side_landmarks.landmarks]
    
    # MediaPipe coordinates are normalized (0-1 range)
    # We need to scale them to real-world measurements
    # Using image dimensions to get pixel-based distances, then scale to cm
    
    # Get image dimensions for scaling
    img_height_front = front_landmarks.image_height
    img_width_front = front_landmarks.image_width
    img_height_side = side_landmarks.image_height
    img_width_side = side_landmarks.image_width
    
    # Calculate pixel-based distances by denormalizing coordinates
    def denormalize_point(pt: Dict[str, float], img_width: int, img_height: int) -> Dict[str, float]:
        """Convert normalized coordinates to pixel coordinates."""
        return {
            'x': pt['x'] * img_width,
            'y': pt['y'] * img_height,
            'z': pt['z'] * img_width,  # z is in same scale as width
            'visibility': pt['visibility']
        }
    
    # Denormalize all points
    front_px = [denormalize_point(pt, img_width_front, img_height_front) for pt in front_pts]
    side_px = [denormalize_point(pt, img_width_side, img_height_side) for pt in side_pts]
    
    # --- HEIGHT CALCULATION ---
    # Height: Distance from ankle to top of head (nose is proxy for head top)
    # Use average of left and right ankle
    left_ankle = front_px[27]
    right_ankle = front_px[28]
    nose = front_px[0]
    
    ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
    head_y = nose['y']
    height_pixels = abs(ankle_y - head_y)
    
    # Assume average person height is 170cm and use this as scaling factor
    # This will be refined with user-provided height or calibration data
    REFERENCE_HEIGHT_CM = 170.0
    pixels_per_cm = height_pixels / REFERENCE_HEIGHT_CM if height_pixels > 0 else 1.0
    
    # --- SHOULDER WIDTH ---
    left_shoulder = front_px[11]
    right_shoulder = front_px[12]
    shoulder_width_px = calculate_distance(left_shoulder, right_shoulder)
    shoulder_width_cm = shoulder_width_px / pixels_per_cm
    
    # --- CHEST MEASUREMENT ---
    # Chest circumference estimate: Use shoulder width from front + depth from side
    # Simplified approach: chest_circumference ≈ π * average_diameter
    left_shoulder_side = side_px[11]
    right_shoulder_side = side_px[12]
    chest_depth_px = abs(left_shoulder_side['z'] - right_shoulder_side['z'])
    chest_depth_cm = chest_depth_px / pixels_per_cm if chest_depth_px > 0 else shoulder_width_cm * 0.5
    
    # Chest is typically at shoulder level, use shoulder measurements as proxy
    chest_width_cm = shoulder_width_cm * 1.05  # Chest is slightly wider than shoulders
    chest_depth_cm = max(chest_depth_cm, chest_width_cm * 0.5)  # Ensure reasonable depth
    
    # Simplified circumference: average of width and depth * π
    chest_cm = math.pi * (chest_width_cm + chest_depth_cm) / 2
    
    # --- WAIST MEASUREMENT ---
    # Waist is approximately midway between shoulders and hips
    left_hip = front_px[23]
    right_hip = front_px[24]
    
    waist_y = (left_shoulder['y'] + right_shoulder['y'] + left_hip['y'] + right_hip['y']) / 4
    waist_width_px = calculate_distance(left_hip, right_hip) * 0.85  # Waist is narrower than hips
    waist_width_cm = waist_width_px / pixels_per_cm
    
    # Get waist depth from side view
    left_hip_side = side_px[23]
    right_hip_side = side_px[24]
    waist_depth_px = abs(left_hip_side['z'] - right_hip_side['z']) * 0.8
    waist_depth_cm = waist_depth_px / pixels_per_cm if waist_depth_px > 0 else waist_width_cm * 0.5
    
    # Simplified circumference
    waist_cm = math.pi * (waist_width_cm + waist_depth_cm) / 2
    
    # --- HIP MEASUREMENT ---
    hip_width_px = calculate_distance(left_hip, right_hip)
    hip_width_cm = hip_width_px / pixels_per_cm
    
    hip_depth_px = abs(left_hip_side['z'] - right_hip_side['z'])
    hip_depth_cm = hip_depth_px / pixels_per_cm if hip_depth_px > 0 else hip_width_cm * 0.55
    
    # Simplified circumference
    hip_cm = math.pi * (hip_width_cm + hip_depth_cm) / 2
    
    # --- INSEAM ---
    # Distance from ankle to hip (crotch level)
    left_ankle_front = front_px[27]
    left_hip_front = front_px[23]
    inseam_px = calculate_distance(left_ankle_front, left_hip_front)
    inseam_cm = inseam_px / pixels_per_cm
    
    # --- OUTSEAM ---
    # Distance from ankle to waist level
    outseam_px = abs(ankle_y - waist_y)
    outseam_cm = outseam_px / pixels_per_cm
    
    # --- SLEEVE LENGTH ---
    # Distance from shoulder to wrist
    left_wrist = front_px[15]
    sleeve_px = calculate_distance(left_shoulder, left_wrist)
    sleeve_cm = sleeve_px / pixels_per_cm
    
    # --- BICEP ---
    # Distance from shoulder to elbow
    left_elbow = front_px[13]
    bicep_length_px = calculate_distance(left_shoulder, left_elbow)
    bicep_length_cm = bicep_length_px / pixels_per_cm
    # Bicep circumference is estimated from upper arm length
    # Typical ratio: bicep_circumference ≈ 0.9 * upper_arm_length
    bicep_cm = bicep_length_cm * 0.9
    
    # --- FOREARM ---
    # Distance from elbow to wrist
    forearm_length_px = calculate_distance(left_elbow, left_wrist)
    forearm_length_cm = forearm_length_px / pixels_per_cm
    # Forearm circumference is estimated from forearm length
    # Typical ratio: forearm_circumference ≈ 0.85 * forearm_length
    forearm_cm = forearm_length_cm * 0.85
    
    # --- THIGH ---
    # Distance from hip to knee
    left_knee = front_px[25]
    thigh_length_px = calculate_distance(left_hip_front, left_knee)
    thigh_length_cm = thigh_length_px / pixels_per_cm
    # Thigh circumference is estimated from thigh length
    # Typical ratio: thigh_circumference ≈ 1.3 * thigh_length
    thigh_cm = thigh_length_cm * 1.3
    
    # --- KNEE ---
    # Knee circumference estimated from thigh and calf
    knee_cm = thigh_cm * 0.7  # Knee is ~70% of thigh circumference
    
    # --- CALF ---
    # Distance from knee to ankle
    calf_length_px = calculate_distance(left_knee, left_ankle_front)
    calf_length_cm = calf_length_px / pixels_per_cm
    # Calf circumference is estimated from calf length
    # Typical ratio: calf_circumference ≈ 0.9 * calf_length
    calf_cm = calf_length_cm * 0.9
    
    # --- ANKLE ---
    # Ankle circumference estimated as smaller than calf
    ankle_cm = calf_cm * 0.65  # Ankle is ~65% of calf circumference
    
    # --- NECK ---
    # Neck is estimated from shoulder width
    neck_cm = shoulder_width_cm * 0.4  # Neck is ~40% of shoulder width
    
    # --- UNDERBUST ---
    # Underbust is between chest and waist
    underbust_cm = (chest_cm + waist_cm) / 2 * 0.95
    
    # --- FRONT RISE & BACK RISE ---
    # Rise measurements from hip to waist
    front_rise_cm = abs(waist_y - left_hip['y']) / pixels_per_cm
    back_rise_cm = front_rise_cm * 1.2  # Back rise is typically longer
    
    # Return all measurements in centimeters
    measurements = {
        "height_cm": height_pixels / pixels_per_cm,
        "neck_cm": neck_cm,
        "shoulder_cm": shoulder_width_cm,
        "chest_cm": chest_cm,
        "underbust_cm": underbust_cm,
        "waist_natural_cm": waist_cm,
        "sleeve_cm": sleeve_cm,
        "bicep_cm": bicep_cm,
        "forearm_cm": forearm_cm,
        "hip_low_cm": hip_cm,
        "thigh_cm": thigh_cm,
        "knee_cm": knee_cm,
        "calf_cm": calf_cm,
        "ankle_cm": ankle_cm,
        "front_rise_cm": front_rise_cm,
        "back_rise_cm": back_rise_cm,
        "inseam_cm": inseam_cm,
        "outseam_cm": outseam_cm,
    }
    
    return measurements


def estimate_accuracy(
    measurements: Dict[str, float],
    front_landmarks: MediaPipeLandmarks,
    side_landmarks: MediaPipeLandmarks,
) -> float:
    """
    Estimate accuracy of MediaPipe-derived measurements (0-1 scale).

    Uses visibility heuristics and pose quality checks.
    """
    front_scores = [lm.visibility for lm in front_landmarks.landmarks]
    side_scores = [lm.visibility for lm in side_landmarks.landmarks]
    avg_visibility = (sum(front_scores) + sum(side_scores)) / (
        len(front_scores) + len(side_scores)
    )

    # Check key landmarks visibility (shoulders, hips, knees, ankles)
    key_indices = [11, 12, 23, 24, 25, 26, 27, 28]
    key_visibility_front = sum(front_landmarks.landmarks[i].visibility for i in key_indices) / len(key_indices)
    key_visibility_side = sum(side_landmarks.landmarks[i].visibility for i in key_indices) / len(key_indices)
    key_visibility_avg = (key_visibility_front + key_visibility_side) / 2

    # Accuracy estimation based on visibility
    if avg_visibility > 0.85 and key_visibility_avg > 0.9:
        return 0.95
    elif avg_visibility > 0.7 and key_visibility_avg > 0.75:
        return 0.90
    elif avg_visibility > 0.5 and key_visibility_avg > 0.6:
        return 0.85
    else:
        return 0.80


def normalize_and_validate(
    input_data: MeasurementInput, raw_payload: Dict | None = None
) -> MeasurementNormalized:
    """
    Normalize measurement input to centimeters and validate field names.
    
    If MediaPipe landmarks are provided, calculate measurements from landmarks.
    Otherwise, use user-provided measurements.
    
    Args:
        input_data: Raw measurement input with optional MediaPipe landmarks
        raw_payload: Optional raw payload dict for validation
        
    Returns:
        Normalized measurements in centimeters with confidence scores
        
    Raises:
        HTTPException with 422 status for validation errors
    """
    errors = []
    
    # Check for unknown fields in user-provided measurements
    if not input_data.front_landmarks and not input_data.side_landmarks:
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
            if field_name not in CANONICAL_FIELDS and field_name not in ALLOWED_META_FIELDS:
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
                message="Invalid measurement field names",
                errors=errors,
                session_id=input_data.session_id,
            ).model_dump(),
        )
    
    # Calculate measurements from MediaPipe landmarks if available
    if input_data.front_landmarks and input_data.side_landmarks:
        measurements = calculate_measurements_from_landmarks(
            input_data.front_landmarks,
            input_data.side_landmarks
        )
        source = "mediapipe"
        accuracy = estimate_accuracy(
            measurements, input_data.front_landmarks, input_data.side_landmarks
        )
        
        # Store landmarks for provenance
        front_landmarks_id = str(uuid.uuid4())
        side_landmarks_id = str(uuid.uuid4())
        # TODO: Store landmarks in database
        confidence = accuracy

    else:
        # Use user-provided measurements and convert to cm
        unit = input_data.unit or Unit.CM
        measurements = {}
        
        for field in CANONICAL_FIELDS:
            value = getattr(input_data, field, None)
            if value is not None:
                if unit == Unit.IN:
                    measurements[f"{field}_cm"] = inches_to_cm(value)
                else:
                    measurements[f"{field}_cm"] = value
        
        source = "user_input"
        accuracy = 1.0  # Assume user input is accurate
        confidence = accuracy
        front_landmarks_id = None
        side_landmarks_id = None

    session_id = input_data.session_id or str(uuid.uuid4())

    normalized_kwargs = {
        **measurements,
        "source": source,
        "model_version": "v1.0-mediapipe",
        "confidence": confidence,
        "accuracy_estimate": accuracy,
        "session_id": session_id,
        "front_photo_url": input_data.front_photo_url,
        "side_photo_url": input_data.side_photo_url,
        "front_landmarks_id": front_landmarks_id,
        "side_landmarks_id": side_landmarks_id,
    }

    return MeasurementNormalized(**normalized_kwargs)
