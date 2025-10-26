from pydantic import BaseModel, Field
from typing import List

class MeasurementModel(BaseModel):
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
    source: str
    vendor_version: str
    confidence: float = Field(ge=0, le=1)


class MeasurementsResponse(BaseModel):
    status: str
    data: MeasurementModel


class RecommendationModel(BaseModel):
    category: str
    size: str
    confidence: float = Field(ge=0, le=1)
    rationale: str


class DMAASResponse(BaseModel):
    measurement: MeasurementModel
    recommendations: List[RecommendationModel]
