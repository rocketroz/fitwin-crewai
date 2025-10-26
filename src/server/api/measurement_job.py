from fastapi import APIRouter
from src.server.normalize import normalize_vendor
from src.server.models import MeasurementsResponse
from src.server.settings import settings

# Conditional vendor client selection based on VENDOR_MODE
if settings.vendor_mode == "stub":
    from src.server.vendor_client import fetch_two_photo_stub as fetch_measurements
else:
    # Placeholder for real vendor client implementation
    from src.server.vendor_client import fetch_real_vendor as fetch_measurements

router = APIRouter(prefix="/measurements", tags=["measurements"])


@router.get("/", response_model=MeasurementsResponse)
def get_measurements():
    vendor = fetch_measurements(session_id="local-test")
    m = normalize_vendor(vendor).as_dict()
    return {"status": "success", "data": m}
