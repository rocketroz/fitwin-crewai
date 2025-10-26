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

    Returns a small dictionary indicating not-implemented so callers can handle it.
    Replace this with a real HTTP client calling your vendor API and returning the
    vendor-specific payload expected by `normalize_vendor`.
    """
    return {
        "error": "not_implemented",
        "message": "fetch_real_vendor is a placeholder. Implement real vendor integration.",
        "session_id": session_id,
    }
