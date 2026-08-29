"""
Products API Router.
"""

from typing import Optional
from fastapi import APIRouter, Query, Path
from backend.api.schemas.products import ProductListResponse, ProductSchema
from backend.api.services.product_service import get_products, get_product_by_id

router = APIRouter(tags=["Products"])

@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="List Smartphone Catalog SKUs",
    description="Retrieve product SKUs with optional market segment and lifecycle stage filters.",
)
def list_products(
    segment: Optional[str] = Query(None, description="Filter products by segment (Budget, Mid-Range, Premium, Flagship)", examples=["Budget"]),
    lifecycle_stage: Optional[str] = Query(None, description="Filter products by lifecycle stage (Launch, Growth, Peak, Decline, EOL)", examples=["Peak"]),
) -> ProductListResponse:
    products, count = get_products(segment=segment, lifecycle_stage=lifecycle_stage)
    return ProductListResponse(
        products=[ProductSchema(**p) for p in products],
        count=count,
    )

@router.get(
    "/products/{product_id}",
    response_model=ProductSchema,
    summary="Get Product Details by SKU ID",
    description="Retrieve single product details by product_id (e.g. PROD_001). Returns 404 if missing.",
)
def get_product(
    product_id: str = Path(..., description="Unique Product SKU ID", examples=["PROD_001"]),
) -> ProductSchema:
    product = get_product_by_id(product_id)
    return ProductSchema(**product)
