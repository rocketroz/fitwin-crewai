from fastapi import FastAPI
from src.server.api.measurement_job import router as measurements
from src.server.api.dmaas import router as dmaas

app = FastAPI(title="FitTwin Local Stub")
app.include_router(measurements)
app.include_router(dmaas)
