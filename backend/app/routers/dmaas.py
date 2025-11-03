from fastapi import APIRouter
from backend.app.services.vendor_client import fetch_two_photo_stub
from backend.app.core.utils import normalize_vendor
from backend.app.services.fit_rules_tops import recommend_top
from backend.app.services.fit_rules_bottoms import recommend_bottom
from backend.app.schemas.models import DMAASResponse

router = APIRouter(prefix="/dmaas", tags=["dmaas"])

@router.get("/latest", response_model=DMAASResponse)
def latest():
    vendor = fetch_two_photo_stub(session_id="local-test")
    m = normalize_vendor(vendor).as_dict()
    recs = [recommend_top(m), recommend_bottom(m)]
    return {"measurement": m, "recommendations": recs}
