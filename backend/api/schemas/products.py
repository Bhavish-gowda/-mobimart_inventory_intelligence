"""
Pydantic Schemas for Product Endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class ProductSchema(BaseModel):
    id: str = Field(..., description="Unique product SKU identifier", example="PROD_001")
    brand: Optional[str] = Field(None, description="Product brand name", example="Nova")
    model_name: str = Field(..., description="Product model name", example="Nova Go 4G")
    segment: str = Field(..., description="Product market segment (Budget, Mid-Range, Premium, Flagship)", example="Budget")
    cost_price: float = Field(..., description="Unit cost price in INR", example=6500.0)
    retail_price: float = Field(..., description="Unit retail price in INR", example=7800.0)
    lifecycle_stage: str = Field(..., description="Product lifecycle stage (Launch, Growth, Peak, Decline, EOL)", example="Peak")
    markdown_percentage: Optional[float] = Field(0.0, description="Standard markdown percentage", example=0.0)
    successor_product_id: Optional[str] = Field(None, description="Successor product SKU ID if defined", example="PROD_002")
    expected_successor_week: Optional[float] = Field(None, description="Expected successor launch week", example=30.0)
    launch_confidence: Optional[float] = Field(1.0, description="Launch confidence factor (0.0 - 1.0)", example=1.0)
    is_rumoured: Optional[bool] = Field(False, description="Whether successor launch is rumoured", example=False)

    @field_validator("successor_product_id", mode="before")
    @classmethod
    def sanitize_successor_id(cls, v):
        """Convert NaN/None/empty to None."""
        if v is None:
            return None
        try:
            import math
            if isinstance(v, float) and math.isnan(v):
                return None
        except Exception:
            pass
        val = str(v).strip()
        return val if val and val.lower() not in ("nan", "none", "") else None

    @field_validator("expected_successor_week", mode="before")
    @classmethod
    def sanitize_successor_week(cls, v):
        """Convert NaN/None to None."""
        if v is None:
            return None
        try:
            import math
            if isinstance(v, float) and math.isnan(v):
                return None
        except Exception:
            pass
        return v

class ProductListResponse(BaseModel):
    products: List[ProductSchema]
    count: int = Field(..., description="Total products matching filter criteria", example=60)
