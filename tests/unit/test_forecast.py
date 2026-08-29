"""
Pytest unit tests for Demand Forecasting Module.
Verifies forecast non-negativity, zero-history handling, sales velocity influence,
seasonality waves, and lifecycle stage factors. Zero future data leakage.
"""

import pytest
import pandas as pd
from backend.engine.allocation.forecast import (
    forecast_weekly_demand,
    get_recent_sales_velocity,
    get_rolling_average,
    get_seasonal_factor,
    get_lifecycle_factor,
)

@pytest.fixture
def mock_sales_history():
    data = []
    # Store 1, Prod 1: High sales history
    for wk in range(1, 20):
        data.append({"store_id": "STORE_01", "product_id": "PROD_001", "week_number": wk, "units_sold": 10})
    # Store 1, Prod 2: Zero sales history
    for wk in range(1, 20):
        data.append({"store_id": "STORE_01", "product_id": "PROD_002", "week_number": wk, "units_sold": 0})
    return pd.DataFrame(data)

def test_forecast_non_negative(mock_sales_history):
    """Forecast must always be non-negative."""
    store = {"id": "STORE_01", "budget_affinity": 1.0, "mid_range_affinity": 1.0}
    product = {"id": "PROD_001", "segment": "Budget", "lifecycle_stage": "Peak"}
    fc = forecast_weekly_demand(mock_sales_history, store, product, current_week=20)
    assert fc.forecast_weekly_demand >= 0.0

def test_zero_history_handled_safely(mock_sales_history):
    """Zero sales history must not crash and produce safe baseline forecast."""
    store = {"id": "STORE_01", "budget_affinity": 1.0}
    product = {"id": "PROD_002", "segment": "Budget", "lifecycle_stage": "Launch"}
    fc = forecast_weekly_demand(mock_sales_history, store, product, current_week=20)
    assert fc.forecast_weekly_demand > 0.0  # Launch SKU receives positive baseline

def test_recent_sales_influences_forecast(mock_sales_history):
    """Higher historical sales velocity must produce higher forecasted demand."""
    store = {"id": "STORE_01", "budget_affinity": 1.0}
    prod1 = {"id": "PROD_001", "segment": "Budget", "lifecycle_stage": "Peak"}
    prod2 = {"id": "PROD_002", "segment": "Budget", "lifecycle_stage": "Peak"}

    fc1 = forecast_weekly_demand(mock_sales_history, store, prod1, current_week=20)
    fc2 = forecast_weekly_demand(mock_sales_history, store, prod2, current_week=20)

    assert fc1.forecast_weekly_demand > fc2.forecast_weekly_demand

def test_seasonality_influences_forecast():
    """Festive weeks (W41, W42) must produce higher seasonal multipliers."""
    normal_s = get_seasonal_factor(week=15)
    diwali_s = get_seasonal_factor(week=42)
    assert diwali_s > normal_s

def test_lifecycle_influences_forecast():
    """Launch/Growth lifecycle stages must have higher lifecycle factors than EOL."""
    prod_launch = {"lifecycle_stage": "Launch"}
    prod_eol = {"lifecycle_stage": "EOL"}

    f_launch = get_lifecycle_factor(prod_launch, current_week=10)
    f_eol = get_lifecycle_factor(prod_eol, current_week=10)

    assert f_launch > f_eol

def test_observed_zero_sales_does_not_trigger_cold_start_surge(mock_sales_history):
    """An established non-Launch product with observed 0 sales must forecast 0 demand, not a cold-start surge."""
    store = {"id": "STORE_01", "budget_affinity": 1.0, "mid_range_affinity": 1.0}
    product = {"id": "PROD_002", "segment": "Mid-Range", "lifecycle_stage": "Peak"}
    fc = forecast_weekly_demand(mock_sales_history, store, product, current_week=20)
    assert fc.forecast_weekly_demand == 0.0
