"""Compatibility layer to expose the FastAPI app under ``src.server.main``."""

from backend.app.main import app

__all__ = ("app",)

