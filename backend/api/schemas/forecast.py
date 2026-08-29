"""
Pydantic Schemas for Forecast Endpoints.
"""

from pydantic import BaseModel, Field

class ForecastRequest(BaseModel):
    store_id: str = Field(..., description="Store ID for forecast", example="STORE_01")
    product_id: str = Field(..., description="Product SKU ID for forecast", example="PROD_001")
    planning_week: int = Field(..., ge=1, le=52, description="Target planning week W (1-52)", example=24)

class ForecastResponse(BaseModel):
    store_id: str
    product_id: str
    planning_week: int
    forecast_weekly_demand: float = Field(..., description="Forecasted weekly customer demand units")
    recent_sales_velocity: float = Field(..., description="Recent 3-week sales velocity")
    rolling_avg: float = Field(..., description="Historical 6-week rolling average")
    trend_factor: float = Field(..., description="Sales trend multiplier")
    seasonal_factor: float = Field(..., description="Festive/seasonality factor")
    lifecycle_factor: float = Field(..., description="Product lifecycle stage factor")
    affinity_factor: float = Field(..., description="Store-segment affinity factor")
    confidence: float = Field(..., description="Forecast confidence score (0.0 - 1.0)")
