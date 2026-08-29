"""
Stores API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query, Path
from backend.api.schemas.stores import StoreListResponse, StoreSchema
from backend.api.services.store_service import get_stores

router = APIRouter(tags=["Stores"])

@router.get(
    "/stores",
    response_model=StoreListResponse,
    summary="List MobiMart Stores",
    description="Retrieve all MobiMart stores across Karnataka with optional city and location type filters.",
)
def list_stores(
    city: Optional[str] = Query(None, description="Filter stores by city name (e.g., Bangalore, Mysore)", examples=["Bangalore"]),
    location_type: Optional[str] = Query(None, description="Filter stores by location type (e.g., High Street, Mall)", examples=["High Street"]),
) -> StoreListResponse:
    stores, count = get_stores(city=city, location_type=location_type)
    return StoreListResponse(
        stores=[StoreSchema(**s) for s in stores],
        count=count,
    )

@router.get(
    "/stores/{store_id}",
    response_model=StoreSchema,
    summary="Get Store Details by ID",
    description="Retrieve single store details by store_id (e.g. STORE_01). Returns 404 if missing.",
)
def get_store(
    store_id: str = Path(..., description="Unique Store ID", examples=["STORE_01"]),
) -> StoreSchema:
    from backend.api.services.store_service import get_store_by_id
    store = get_store_by_id(store_id)
    return StoreSchema(**store)
