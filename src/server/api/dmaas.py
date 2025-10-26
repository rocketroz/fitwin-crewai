from fastapi import APIRouter
from src.server.vendor_client import fetch_two_photo_stub
from src.server.normalize import normalize_vendor
from src.server.fit_rules_tops import recommend_top
from src.server.fit_rules_bottoms import recommend_bottom
from src.server.models import DMAASResponse

router = APIRouter(prefix="/dmaas", tags=["dmaas"])

@router.get("/latest", response_model=DMAASResponse)
def latest():
    vendor = fetch_two_photo_stub(session_id="local-test")
    m = normalize_vendor(vendor).as_dict()
    recs = [recommend_top(m), recommend_bottom(m)]
    return {"measurement": m, "recommendations": recs}
