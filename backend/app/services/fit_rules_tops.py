from typing import Dict
INCH = 1/2.54

def recommend_top(m: Dict) -> Dict:
    chest_in = round(m["chest_cm"] * INCH)
    shoulder_in = round(m["shoulder_cm"] * INCH)
    sleeve_in = round(m["sleeve_cm"] * INCH)
    # simple S/M/L mapping placeholder
    if chest_in <= 36: size = "S"
    elif chest_in <= 40: size = "M"
    elif chest_in <= 44: size = "L"
    else: size = "XL"
    rationale = f"Based on chest {chest_in} in, shoulder {shoulder_in} in, sleeve {sleeve_in} in"
    return {"category": "top", "size": size, "confidence": 0.7, "rationale": rationale}
