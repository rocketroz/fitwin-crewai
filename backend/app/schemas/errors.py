"""Shared error envelope schemas for API responses."""

from typing import List, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Granular validation or server error information."""

    field: str
    message: str
    hint: Optional[str] = None


class ErrorResponse(BaseModel):
    """Top-level error envelope aligned with Manus package contract."""

    type: str
    code: str
    message: str
    errors: List[ErrorDetail]
    session_id: Optional[str] = None
