"""
Measurement schemas for input validation and normalization.

This module defines the canonical measurement names, unit enum, and schemas
for input, MediaPipe landmarks, and normalized output.
"""

from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional, List


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
    
    # Photo URLs (for storage and future model training)
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None
    
    # Device metadata
    device_id: Optional[str] = None

    class Config:
        extra = "allow"

    @validator('*', pre=True)
    def check_positive(cls, v, field):
        """Validate that numeric measurements are positive."""
        if field.name in ['unit', 'session_id', 'front_landmarks', 'side_landmarks', 
                          'front_photo_url', 'side_photo_url']:
            return v
        if v is not None and isinstance(v, (int, float)) and v <= 0:
            raise ValueError(f"{field.name} must be positive")
        return v


class MeasurementNormalized(BaseModel):
    """Normalized measurement schema (all in cm) with confidence scores."""
    height_cm: float
    neck_cm: float
    shoulder_cm: float
    chest_cm: float
    underbust_cm: float
    waist_natural_cm: float
    sleeve_cm: float
    bicep_cm: float
    forearm_cm: float
    hip_low_cm: float
    thigh_cm: float
    knee_cm: float
    calf_cm: float
    ankle_cm: float
    front_rise_cm: float
    back_rise_cm: float
    inseam_cm: float
    outseam_cm: float
    
    # Metadata
    source: str = "mediapipe"  # "mediapipe", "user_input", "vendor_api"
    model_version: str = "v1.0-mediapipe"
    confidence: float = Field(ge=0, le=1, default=1.0)
    accuracy_estimate: Optional[float] = None  # Estimated % error
    session_id: Optional[str] = None
    
    # Provenance
    front_photo_url: Optional[str] = None
    side_photo_url: Optional[str] = None
    front_landmarks_id: Optional[str] = None  # Reference to stored landmarks
    side_landmarks_id: Optional[str] = None

