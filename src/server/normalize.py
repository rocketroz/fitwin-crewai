from src.server.measure_schema import BodyMeasurements

def normalize_vendor(vendor: dict) -> BodyMeasurements:
    v = vendor
    return BodyMeasurements(
        neck_cm=v["neck"]["value"],
        shoulder_cm=v["shoulder"]["value"],
        chest_cm=v["chest"]["value"],
        underbust_cm=v.get("underbust", {"value": v["chest"]["value"] * 0.9})["value"],
        waist_natural_cm=v["waist"]["value"],
        sleeve_cm=v["sleeve"]["value"],
        bicep_cm=v["bicep"]["value"],
        forearm_cm=v["forearm"]["value"],
        hip_low_cm=v["hip_low"]["value"],
        thigh_cm=v["thigh"]["value"],
        knee_cm=v["knee"]["value"],
        calf_cm=v["calf"]["value"],
        ankle_cm=v["ankle"]["value"],
        front_rise_cm=v["front_rise"]["value"],
        back_rise_cm=v["back_rise"]["value"],
        inseam_cm=v["inseam"]["value"],
        outseam_cm=v["outseam"]["value"],
        source="vendor",
        vendor_version=v.get("source_version","unknown"),
        confidence=0.92
    )
