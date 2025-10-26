def fetch_two_photo_stub(session_id: str) -> dict:
    return {
        "neck": {"value": 35.0}, "shoulder": {"value": 44.0},
        "chest": {"value": 96.0}, "underbust": {"value": 84.0},
        "waist": {"value": 82.5}, "sleeve": {"value": 61.0},
        "bicep": {"value": 31.0}, "forearm": {"value": 26.0},
        "hip_low": {"value": 98.0}, "thigh": {"value": 56.0},
        "knee": {"value": 39.0}, "calf": {"value": 36.0}, "ankle": {"value": 23.0},
        "front_rise": {"value": 27.5}, "back_rise": {"value": 36.0},
        "inseam": {"value": 76.0}, "outseam": {"value": 100.0},
        "source_version": "stub-2photo"
    }


def fetch_real_vendor(session_id: str) -> dict:
    """Placeholder for a real vendor client.

    Returns a vendor-shaped payload with None values to indicate the integration
    is not yet implemented. This avoids KeyError during normalization while
    making it explicit the values are missing.
    Replace this with a real HTTP client calling your vendor API and returning the
    vendor-specific payload expected by `normalize_vendor`.
    """
    keys = [
        "neck","shoulder","chest","underbust","waist","sleeve","bicep","forearm",
        "hip_low","thigh","knee","calf","ankle","front_rise","back_rise","inseam","outseam"
    ]
    return {k: {"value": None} for k in keys} | {"source_version": "real-placeholder", "session_id": session_id}
