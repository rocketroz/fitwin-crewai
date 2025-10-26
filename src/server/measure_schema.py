from dataclasses import dataclass
from typing import Dict

@dataclass
class BodyMeasurements:
    # upper body
    neck_cm: float
    shoulder_cm: float              # acromion to acromion
    chest_cm: float                 # bust/chest at fullest
    underbust_cm: float
    waist_natural_cm: float
    sleeve_cm: float                # shoulder to wrist along arm
    bicep_cm: float
    forearm_cm: float

    # lower body
    hip_low_cm: float               # around seat
    thigh_cm: float                 # highest thigh
    knee_cm: float
    calf_cm: float
    ankle_cm: float
    front_rise_cm: float
    back_rise_cm: float
    inseam_cm: float                # crotch to floor
    outseam_cm: float               # waist to floor

    # meta
    source: str
    vendor_version: str
    confidence: float

    def as_dict(self) -> Dict:
        return self.__dict__
