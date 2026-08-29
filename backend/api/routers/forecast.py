"""
Demand Forecast API Router.
"""

from fastapi import APIRouter
from backend.api.schemas.forecast import ForecastRequest, ForecastResponse
from backend.api.services.forecast_service import generate_forecast

router = APIRouter(tags=["Forecasting"])

@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate Historical-Only Demand Forecast (GET Query)",
    description="Forecast weekly demand for a store-product pair at planning week W using zero future leakage.",
)
def get_forecast_query(
    store_id: str,
    product_id: str,
    planning_week: int = 24,
) -> ForecastResponse:
    res = generate_forecast(store_id=store_id, product_id=product_id, planning_week=planning_week)
    return ForecastResponse(
        store_id=res.store_id,
        product_id=res.product_id,
        planning_week=planning_week,
        forecast_weekly_demand=round(res.forecast_weekly_demand, 2),
        recent_sales_velocity=round(res.recent_sales_velocity, 2),
        rolling_avg=round(res.rolling_avg, 2),
        trend_factor=round(res.trend_factor, 2),
        seasonal_factor=round(res.seasonal_factor, 2),
        lifecycle_factor=round(res.lifecycle_factor, 2),
        affinity_factor=round(res.affinity_factor, 2),
        confidence=round(res.confidence, 2),
    )

@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate Historical-Only Demand Forecast (POST Body)",
    description="Forecast weekly demand for a store-product pair at planning week W using zero future leakage.",
)
def create_forecast(request: ForecastRequest) -> ForecastResponse:
    res = generate_forecast(
        store_id=request.store_id,
        product_id=request.product_id,
        planning_week=request.planning_week,
    )
    return ForecastResponse(
        store_id=res.store_id,
        product_id=res.product_id,
        planning_week=request.planning_week,
        forecast_weekly_demand=round(res.forecast_weekly_demand, 2),
        recent_sales_velocity=round(res.recent_sales_velocity, 2),
        rolling_avg=round(res.rolling_avg, 2),
        trend_factor=round(res.trend_factor, 2),
        seasonal_factor=round(res.seasonal_factor, 2),
        lifecycle_factor=round(res.lifecycle_factor, 2),
        affinity_factor=round(res.affinity_factor, 2),
        confidence=round(res.confidence, 2),
    )
