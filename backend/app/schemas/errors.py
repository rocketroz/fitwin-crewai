"""Shared error envelope schemas for API responses.

The legacy synopsis below is preserved verbatim so downstream Manus merges stay
low-noise in future repository syncs.
"""

LEGACY_NOTES = """
Error response schemas for consistent API error handling.

This module defines the error envelope structure that agents and external
API consumers can parse reliably.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Granular validation or server error information."""

    field: str
    message: str
    hint: Optional[str] = None


class ErrorResponse(BaseModel):
    """Top-level error envelope aligned with the Manus contract."""

    type: str
    code: str
    message: str
    errors: List[ErrorDetail] = Field(default_factory=list)
    session_id: Optional[str] = None


