import os
import httpx

BASE_URL = os.getenv("FITWIN_API_URL", "http://127.0.0.1:8000")

def dmaas_latest() -> dict:
    """Fetch latest DMAAS payload from the running FastAPI service."""
    with httpx.Client(timeout=10.0) as c:
        r = c.get(f"{BASE_URL}/dmaas/latest")
        r.raise_for_status()
        return r.json()
import os, httpx

BASE_URL = os.getenv("FITWIN_API_URL", "http://127.0.0.1:8000")

def dmaas_latest() -> dict:
    with httpx.Client(timeout=10.0) as c:
        r = c.get(f"{BASE_URL}/dmaas/latest")
        r.raise_for_status()
        return r.json()
