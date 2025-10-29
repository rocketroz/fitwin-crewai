"""
Measurement schemas for validation, normalization, and MediaPipe landmark input.

Adopted from the Manus implementation package. Uses Pydantic models so the same
schema can serve both API responses and agent tooling.
"""

from __future__ import annotations

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
    """Input schema for measurements with flexible units and MediaPipe data from all platforms."""
    
    # Platform identification
    source_type: str = "mediapipe_web"  # "arkit_lidar", "mediapipe_native", "mediapipe_web", "user_input"
    platform: str = "web_mobile"  # "ios", "android", "web_mobile", "web_desktop"
    
    # ARKit LiDAR data (iOS native only)
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
    processing_location: Optional[str] = None  # "client", "server"

    # Photo URLs for provenance
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None

    # Device metadata
    device_id: Optional[str] = None

    # Validation removed for Pydantic v2 compatibility
    # Field-level validation can be added if needed

    if ConfigDict:  # pragma: no branch - executed depending on pydantic version
        model_config = ConfigDict(extra="allow")
    else:
        class Config:  # type: ignore
            extra = "allow"


class MeasurementNormalized(BaseModel):
    """Normalized measurement schema (all in cm) with confidence scores."""
    
    session_id: str
    measurements: dict  # Dictionary of measurement_name_cm: value
    source: str  # "mediapipe", "user_input", "vendor_api"
    accuracy: float = Field(ge=0, le=1, default=1.0)
    
    # Provenance
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None
    front_landmarks_id: Optional[str] = None
    side_landmarks_id: Optional[str] = None
