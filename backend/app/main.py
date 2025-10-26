from fastapi import FastAPI
from backend.app.routers.measurement_job import router as measurements
from backend.app.routers.dmaas import router as dmaas

app = FastAPI(title="FitTwin Local Stub")
app.include_router(measurements)
app.include_router(dmaas)
