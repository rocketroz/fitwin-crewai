from typing import Dict
INCH = 1/2.54

def recommend_bottom(m: Dict) -> Dict:
    waist = round(m["waist_natural_cm"] * INCH)
    inseam = round(m["inseam_cm"] * INCH)
    notes = []
    if m["thigh_cm"]/m["hip_low_cm"] > 0.58: notes.append("roomy thigh")
    if m["knee_cm"]/m["thigh_cm"] < 0.67: notes.append("strong knee taper")
    rationale = ", ".join(notes) or "standard ease"
    return {"category": "bottom", "size": f"{waist}x{inseam}", "confidence": 0.72, "rationale": rationale}
