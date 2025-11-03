"""
Error response schemas for consistent API error handling.

This module defines the error envelope structure that agents and external
API consumers can parse reliably.
"""

from typing import List, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Detailed error information for a specific field or issue."""

    field: str
    message: str
    hint: Optional[str] = None


class ErrorResponse(BaseModel):
    """Consistent error response envelope for all API errors."""

    type: str  # e.g., "validation_error", "server_error", "authentication_error"
    code: str  # e.g., "schema", "unit", "unknown_field", "accuracy_threshold"
    message: str
    errors: List[ErrorDetail] = []
    session_id: Optional[str] = None
