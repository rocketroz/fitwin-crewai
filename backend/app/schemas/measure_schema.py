"""Measurement schemas for validation and normalization.

The additional legacy synopsis is kept intact below so that future merges with
the Manus repository stay low-noise.
"""

from __future__ import annotations

LEGACY_NOTES = """
Measurement schemas for input validation and normalization.

This module defines the canonical measurement names, unit enum, and schemas
for input, MediaPipe landmarks, and normalized output.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

try:  # Pydantic v2 support
    from pydantic import ConfigDict  # type: ignore
except ImportError:  # pragma: no cover - pydantic v1 fallback
    ConfigDict = None


class Unit(str, Enum):
    """Supported measurement units."""

    CM = "cm"
    IN = "in"


class MediaPipeLandmark(BaseModel):
    """Single MediaPipe landmark with 3D coordinates."""

    x: float
    y: float
    z: float
    visibility: float


class MediaPipeLandmarks(BaseModel):
    """Complete set of MediaPipe Pose landmarks."""

    landmarks: List[MediaPipeLandmark]
    timestamp: str
    image_width: int
    image_height: int


class MeasurementInput(BaseModel):
    """Input schema for measurements with flexible units and MediaPipe data."""

    # Platform identification metadata
    source_type: str = "mediapipe_web"
    platform: str = "web_mobile"

    # Optional ARKit LiDAR data (iOS native)
    arkit_body_anchor: Optional[dict] = None
    arkit_depth_map: Optional[str] = None

    # Core measurements (optional, can be calculated from landmarks)
    height: Optional[float] = None
    neck: Optional[float] = None
    shoulder: Optional[float] = None
    chest: Optional[float] = None
    underbust: Optional[float] = None
    waist_natural: Optional[float] = None
    sleeve: Optional[float] = None
    bicep: Optional[float] = None
    forearm: Optional[float] = None
    hip_low: Optional[float] = None
    thigh: Optional[float] = None
    knee: Optional[float] = None
    calf: Optional[float] = None
    ankle: Optional[float] = None
    front_rise: Optional[float] = None
    back_rise: Optional[float] = None
    inseam: Optional[float] = None
    outseam: Optional[float] = None

    # Unit and metadata
    unit: Unit = Unit.CM
    session_id: Optional[str] = None

    # MediaPipe data (native apps + web)
    front_landmarks: Optional[MediaPipeLandmarks] = None
    side_landmarks: Optional[MediaPipeLandmarks] = None

    # Web-specific metadata
    browser_info: Optional[dict] = None
    processing_location: Optional[str] = None

    # Photo URLs for provenance
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None

    # Device metadata
    device_id: Optional[str] = None

    @field_validator(
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
        mode="before",
    )
    def _ensure_positive(cls, value):
        """Ensure numeric measurements are positive when provided."""

        if value is None:
            return value
        if isinstance(value, (int, float)) and value <= 0:
            raise ValueError("measurements must be positive values")
        return value

    if ConfigDict:  # pragma: no branch - executed depending on pydantic version
        model_config = ConfigDict(extra="allow")
    else:

        class Config:  # type: ignore
            extra = "allow"


class MeasurementNormalized(BaseModel):
    """Normalized measurement schema (all values in centimeters)."""

    # Measurement values
    height_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    shoulder_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    underbust_cm: Optional[float] = None
    waist_natural_cm: Optional[float] = None
    sleeve_cm: Optional[float] = None
    bicep_cm: Optional[float] = None
    forearm_cm: Optional[float] = None
    hip_low_cm: Optional[float] = None
    thigh_cm: Optional[float] = None
    knee_cm: Optional[float] = None
    calf_cm: Optional[float] = None
    ankle_cm: Optional[float] = None
    front_rise_cm: Optional[float] = None
    back_rise_cm: Optional[float] = None
    inseam_cm: Optional[float] = None
    outseam_cm: Optional[float] = None

    # Metadata
    source: str = "mediapipe"
    model_version: str = "v1.0-mediapipe"
    confidence: float = Field(ge=0, le=1, default=1.0)
    accuracy_estimate: Optional[float] = None
    session_id: Optional[str] = None

    # Provenance
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None
    front_landmarks_id: Optional[str] = None
    side_landmarks_id: Optional[str] = None

    if ConfigDict:  # pragma: no branch - executed depending on pydantic version
        model_config = ConfigDict(extra="allow")
    else:

        class Config:  # type: ignore
            extra = "allow"

