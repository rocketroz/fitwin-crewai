from fastapi import APIRouter
from src.server.vendor_client import fetch_two_photo_stub
from src.server.normalize import normalize_vendor
from src.server.models import MeasurementsResponse

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.get("/", response_model=MeasurementsResponse)
def get_measurements():
    vendor = fetch_two_photo_stub(session_id="local-test")
    m = normalize_vendor(vendor).as_dict()
    return {"status": "success", "data": m}
