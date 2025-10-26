from src.server.measure_schema import BodyMeasurements


def _val(v: dict, key: str):
    """Safe extractor for vendor values: returns the numeric value or None."""
    return v.get(key, {}).get("value") if isinstance(v, dict) else None


def normalize_vendor(vendor: dict) -> BodyMeasurements:
    v = vendor
    chest_val = _val(v, "chest")
    underbust_default = chest_val * 0.9 if chest_val is not None else None

    return BodyMeasurements(
        neck_cm=_val(v, "neck"),
        shoulder_cm=_val(v, "shoulder"),
        chest_cm=chest_val,
        underbust_cm=v.get("underbust", {"value": underbust_default})["value"],
        waist_natural_cm=_val(v, "waist"),
        sleeve_cm=_val(v, "sleeve"),
        bicep_cm=_val(v, "bicep"),
        forearm_cm=_val(v, "forearm"),
        hip_low_cm=_val(v, "hip_low"),
        thigh_cm=_val(v, "thigh"),
        knee_cm=_val(v, "knee"),
        calf_cm=_val(v, "calf"),
        ankle_cm=_val(v, "ankle"),
        front_rise_cm=_val(v, "front_rise"),
        back_rise_cm=_val(v, "back_rise"),
        inseam_cm=_val(v, "inseam"),
        outseam_cm=_val(v, "outseam"),
        source="vendor",
        vendor_version=v.get("source_version", "unknown"),
        confidence=0.92
    )
