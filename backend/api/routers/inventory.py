"""
Inventory API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.api.schemas.inventory import (
    InventoryListResponse,
    InventoryRecordSchema,
    InventorySummaryResponse,
)
from backend.api.services.inventory_service import (
    get_inventory_records,
    get_inventory_summary,
)

router = APIRouter(tags=["Inventory"])

@router.get(
    "/inventory",
    response_model=InventoryListResponse,
    summary="Query Store Inventory Positions",
    description="Retrieve store-product inventory positions with optional store_id and product_id filters.",
)
def list_inventory(
    store_id: Optional[str] = Query(None, description="Filter by store ID", examples=["STORE_01"]),
    product_id: Optional[str] = Query(None, description="Filter by product SKU ID", examples=["PROD_001"]),
    page: Optional[int] = Query(None, ge=1, description="Page number for pagination", examples=[1]),
    page_size: Optional[int] = Query(None, ge=1, le=500, description="Page size for pagination (max 500)", examples=[50]),
) -> InventoryListResponse:
    records, count = get_inventory_records(
        store_id=store_id,
        product_id=product_id,
        page=page,
        page_size=page_size,
    )
    return InventoryListResponse(
        records=[InventoryRecordSchema(**r) for r in records],
        count=count,
        page=page,
        page_size=page_size,
    )

@router.get(
    "/inventory/summary",
    response_model=InventorySummaryResponse,
    summary="Get Chain Inventory Capital & Operational Summary",
    description="Get chain-wide inventory totals, raw cost value, operational target capital, retail value, and headroom.",
)
def inventory_summary() -> InventorySummaryResponse:
    summary_data = get_inventory_summary()
    return InventorySummaryResponse(**summary_data)
