"""
Common Pydantic Schemas.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    service: str = Field(..., example="MobiMart Inventory Intelligence API")
    version: str = Field(..., example="1.0.0")

class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorPayload
