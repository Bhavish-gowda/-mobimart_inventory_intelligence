"""
Health Check Router.
"""

from fastapi import APIRouter
from backend.api.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Get API Health Status",
    description="Returns API status, service name, and version information.",
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="MobiMart Inventory Intelligence API",
        version="1.0.0",
    )

@router.get(
    "/health/ready",
    summary="Get API Readiness Status",
    description="Verifies static data sets are loaded and available.",
)
def get_readiness():
    from backend.api.data_loader import load_stores_list, load_products_list
    stores = load_stores_list()
    products = load_products_list()
    return {
        "status": "ready",
        "data_loaded": True,
        "stores_count": len(stores),
        "products_count": len(products),
    }
