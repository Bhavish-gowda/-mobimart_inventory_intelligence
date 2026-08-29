"""
Forecast Service Layer.
Delegates directly to Phase 3A forecast engine (`forecast_weekly_demand`).
Does NOT duplicate forecasting logic.
"""

from typing import Dict, Any
from backend.api.data_loader import load_sales_history_df, load_stores_list, load_products_list
from backend.api.errors import ResourceNotFoundException
from backend.engine.allocation.forecast import forecast_weekly_demand
from backend.engine.allocation.models import ForecastResult

def generate_forecast(
    store_id: str,
    product_id: str,
    planning_week: int,
) -> ForecastResult:
    stores = load_stores_list()
    products = load_products_list()

    store = next((s for s in stores if s["id"] == store_id), None)
    if not store:
        raise ResourceNotFoundException("Store", store_id)

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise ResourceNotFoundException("Product", product_id)

    sales_df = load_sales_history_df()
    
    # Enforce zero future leakage boundary (pass sales history up to current_week - 1)
    hist_df = sales_df[sales_df["week_number"] < planning_week].copy()

    # Delegate directly to Phase 3A engine
    result = forecast_weekly_demand(
        sales_history_df=hist_df,
        store=store,
        product=product,
        current_week=planning_week,
    )

    return result
