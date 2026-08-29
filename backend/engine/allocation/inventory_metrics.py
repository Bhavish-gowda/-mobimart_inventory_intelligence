"""
Inventory Metrics Module for Allocation Engine.
Calculates weeks of cover, stockout risk scores, inventory values,
and potential lost sales for store-product combinations.
"""

from typing import Dict, Any
import numpy as np
from backend.engine.allocation.models import InventoryMetrics, ForecastResult
from backend.engine.allocation.config import TARGET_WEEKS_OF_COVER

def calculate_weeks_of_cover(stock: int, forecast_weekly_demand: float) -> float:
    """
    Calculate weeks of cover safely handling zero or near-zero demand.
    If demand is zero, returns 99.0 weeks of cover.
    """
    if forecast_weekly_demand <= 0.0:
        return 99.0
    return float(stock / forecast_weekly_demand)

def calculate_stockout_risk_score(stock: int, forecast_weekly_demand: float) -> float:
    """
    Calculate stockout risk score on a 0.0 to 100.0 scale.
    High risk (100.0) when current stock is 0 and forecast demand is high.
    Low risk (0.0) when stock >= 4 weeks of cover.
    """
    if forecast_weekly_demand <= 0.0:
        return 0.0

    woc = calculate_weeks_of_cover(stock, forecast_weekly_demand)
    if woc >= 3.5:
        return 0.0

    # Linear scale from 100 (0 woc) down to 0 (3.5 woc)
    risk = (1.0 - (woc / 3.5)) * 100.0
    return float(np.clip(risk, 0.0, 100.0))

def calculate_inventory_metrics(
    inventory_record: Dict[str, Any],
    forecast_result: ForecastResult,
    product: Dict[str, Any],
    additional_units: int = 0,
) -> InventoryMetrics:
    """
    Calculate complete inventory metrics for store-product pair before and after additional allocation units.
    """
    current_stock = int(inventory_record.get("current_stock", 0))
    in_transit = int(inventory_record.get("in_transit_stock", 0))
    cost_price = float(product["cost_price"])

    projected_stock = current_stock + in_transit + additional_units
    demand = forecast_result.forecast_weekly_demand

    current_woc = calculate_weeks_of_cover(current_stock, demand)
    projected_woc = calculate_weeks_of_cover(projected_stock, demand)
    stockout_risk = calculate_stockout_risk_score(projected_stock, demand)

    potential_lost_sales = max(0.0, demand - projected_stock)
    inventory_val = projected_stock * cost_price

    return InventoryMetrics(
        store_id=inventory_record["store_id"],
        product_id=inventory_record["product_id"],
        current_stock=current_stock,
        in_transit_stock=in_transit,
        projected_stock=projected_stock,
        weeks_of_cover=round(current_woc, 2),
        projected_weeks_of_cover=round(projected_woc, 2),
        inventory_value=round(inventory_val, 2),
        stockout_risk_score=round(stockout_risk, 2),
        potential_lost_sales_units=round(potential_lost_sales, 2),
    )
