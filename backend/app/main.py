"""
FitTwin DMaaS API application entry point.

This FastAPI app exposes measurement validation and recommendation endpoints
backed by MediaPipe landmark processing and normalization utilities.
FitTwin DMaaS API - Main application entry point.

This FastAPI application provides a Data-Model-as-a-Service (DMaaS) API
for accurate body measurements and size recommendations, designed for
AI systems (like ChatGPT-powered shopping assistants) and online retailers.
"""

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
    allow_origins=["*"],
        "Data-Model-as-a-Service API for accurate body measurements and size recommendations. "
        "Designed for AI systems (like ChatGPT-powered shopping assistants) and online retailers. "
        "Uses MediaPipe Pose Landmarker for free, on-device measurement extraction."
    ),
    version="1.0.0-mediapipe-mvp",
    contact={
        "name": "FitTwin Support",
        "email": "support@fittwin.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(measurements_router)


@app.get("/")
def root():
    """Lightweight health probe with docs pointer."""
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "FitTwin DMaaS API is running",
        "version": "1.0.0-mediapipe-mvp",
        "docs": "/docs",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Detailed health probe for monitoring."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: add real DB check
        "mediapipe": "available",
        "version": "1.0.0-mediapipe-mvp",
    """Detailed health check for monitoring."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "mediapipe": "available",
        "version": "1.0.0-mediapipe-mvp"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)

