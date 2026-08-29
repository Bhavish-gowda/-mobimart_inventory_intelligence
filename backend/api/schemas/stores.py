"""
Pydantic Schemas for Store Endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class StoreSchema(BaseModel):
    id: str = Field(..., description="Unique store identifier", example="STORE_01")
    name: str = Field(..., description="Store display name", example="MobiMart Indiranagar 100ft Rd")
    city: str = Field(..., description="Store location city", example="Bangalore")
    location_type: str = Field(..., description="Store location type (High Street, Premium Mall, Mass Market, Tier-2 Center, Tier-3 Center)", example="High Street")
    store_size_sqft: Optional[int] = Field(None, description="Store size in square feet", example=3500)
    monthly_footfall: Optional[int] = Field(None, description="Average monthly store footfall", example=65000)
    income_index: Optional[float] = Field(None, description="City catchment income index", example=1.85)
    budget_affinity: Optional[float] = Field(None, description="Budget segment sales affinity factor", example=0.4)
    mid_range_affinity: Optional[float] = Field(None, description="Mid-Range segment sales affinity factor", example=0.8)
    premium_affinity: Optional[float] = Field(None, description="Premium segment sales affinity factor", example=1.8)
    flagship_affinity: Optional[float] = Field(None, description="Flagship segment sales affinity factor", example=2.2)

class StoreListResponse(BaseModel):
    stores: List[StoreSchema]
    count: int = Field(..., description="Total stores matching filter criteria", example=25)
