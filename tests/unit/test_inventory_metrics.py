"""
Pytest unit tests for Inventory Metrics Module.
Verifies weeks of cover calculation, zero-demand safety, and stockout risk scoring.
"""

import pytest
from backend.engine.allocation.inventory_metrics import (
    calculate_weeks_of_cover,
    calculate_stockout_risk_score,
    calculate_inventory_metrics,
)
from backend.engine.allocation.models import ForecastResult

def test_weeks_of_cover_calculation():
    """Stock / Weekly Demand = Weeks of Cover."""
    woc = calculate_weeks_of_cover(stock=10, forecast_weekly_demand=2.5)
    assert woc == 4.0

def test_zero_demand_handled_safely():
    """Zero demand must return 99.0 weeks of cover and zero stockout risk without crashing."""
    woc = calculate_weeks_of_cover(stock=5, forecast_weekly_demand=0.0)
    assert woc == 99.0

    risk = calculate_stockout_risk_score(stock=5, forecast_weekly_demand=0.0)
    assert risk == 0.0

def test_stockout_risk_increases_with_low_inventory():
    """Low stock relative to demand must produce high stockout risk score."""
    high_stock_risk = calculate_stockout_risk_score(stock=15, forecast_weekly_demand=3.0)  # 5 woc
    low_stock_risk = calculate_stockout_risk_score(stock=1, forecast_weekly_demand=3.0)   # 0.33 woc

    assert high_stock_risk == 0.0
    assert low_stock_risk > 80.0

def test_inventory_metrics_data_structure():
    """Verify InventoryMetrics populated fields."""
    inv_rec = {"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 2, "in_transit_stock": 0}
    product = {"cost_price": 10000.0}
    fc = ForecastResult(
        store_id="STORE_01", product_id="PROD_001", forecast_weekly_demand=10.0,
        recent_sales_velocity=10.0, rolling_avg=10.0, trend_factor=1.0,
        seasonal_factor=1.0, lifecycle_factor=1.0, affinity_factor=1.0, confidence=1.0
    )

    metrics = calculate_inventory_metrics(inv_rec, fc, product, additional_units=3)
    assert metrics.current_stock == 2
    assert metrics.projected_stock == 5
    assert metrics.weeks_of_cover == 0.2
    assert metrics.projected_weeks_of_cover == 0.5
    assert metrics.inventory_value == 50000.0
