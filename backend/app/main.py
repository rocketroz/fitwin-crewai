"""FitTwin DMaaS API application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.measurements import router as measurements_router


app = FastAPI(
    title="FitTwin DMaaS API",
    description=(
        "Data-Model-as-a-Service API for accurate body measurements and size "
        "recommendations. Designed for AI systems and online retailers, powered "
        "by MediaPipe Pose Landmarker extraction."
    ),
    version="1.0.0-mediapipe-mvp",
    contact={"name": "FitTwin Support", "email": "support@fittwin.com"},
    license_info={"name": "Proprietary"},
)

# Allow cross-origin requests during development; tighten when deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(measurements_router)


@app.get("/")
def root():
    """Lightweight readiness probe with docs pointer."""
    return {
        "status": "ok",
        "message": "FitTwin DMaaS API is running",
        "version": "1.0.0-mediapipe-mvp",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Detailed health probe for monitoring."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: add real DB check
        "mediapipe": "available",
        "version": "1.0.0-mediapipe-mvp",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

