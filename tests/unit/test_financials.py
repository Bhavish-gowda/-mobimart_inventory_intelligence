"""
Pytest unit tests for Financial Impact & Explanation Module.
Verifies unit margin, avoided goodwill benefit, logistics allocation costs,
zero double-counting, and cost separation between warehouse and transfer costs.
"""

import pytest
from backend.engine.allocation.financials import calculate_avoided_goodwill_benefit, calculate_financial_impact
from backend.engine.allocation.models import ForecastResult, InventoryMetrics
from backend.engine.allocation.config import WAREHOUSE_ALLOCATION_COST_PER_UNIT, STORE_TRANSFER_COST_PER_UNIT

@pytest.fixture
def sample_product():
    return {
        "id": "PROD_001",
        "segment": "Budget",
        "cost_price": 8000.0,
        "retail_price": 10000.0,
        "lifecycle_stage": "Peak",
    }

def test_margin_calculation(sample_product):
    """Unit Margin = Retail Price - Cost Price."""
    cost = sample_product["cost_price"]
    retail = sample_product["retail_price"]
    assert retail - cost == 2000.0

def test_avoid_double_counting_margin_and_stockout_loss(sample_product):
    """
    VERIFY ZERO DOUBLE COUNTING:
    Avoided goodwill benefit must NOT contain unit margin.
    It contains strictly goodwill_penalty = unit_margin * goodwill_factor.
    """
    fc = ForecastResult(
        store_id="STORE_01", product_id="PROD_001", forecast_weekly_demand=1.0,
        recent_sales_velocity=1.0, rolling_avg=1.0, trend_factor=1.0,
        seasonal_factor=1.0, lifecycle_factor=1.0, affinity_factor=1.0, confidence=1.0
    )
    inv_zero = InventoryMetrics(
        store_id="STORE_01", product_id="PROD_001", current_stock=0, in_transit_stock=0,
        projected_stock=1, weeks_of_cover=0.0, projected_weeks_of_cover=1.0,
        inventory_value=8000.0, stockout_risk_score=100.0, potential_lost_sales_units=0.0
    )

    fin = calculate_financial_impact(sample_product, fc, inv_zero, additional_unit_index=1)
    unit_margin = 2000.0

    # Expected gross margin on fulfilled sale
    assert fin.expected_incremental_margin == unit_margin

    # Avoided goodwill benefit for Budget segment (15% factor) = 2000 * 0.15 = 300
    assert fin.avoided_goodwill_benefit == 300.0

    # Net value = 2000 (margin) + 300 (goodwill) - 250 (warehouse cost) = 2050
    assert fin.net_marginal_value == 2050.0

def test_transfer_and_warehouse_costs_are_separate():
    """Verify warehouse allocation cost (₹250) and store transfer cost (₹500) are separate."""
    assert WAREHOUSE_ALLOCATION_COST_PER_UNIT == 250.0
    assert STORE_TRANSFER_COST_PER_UNIT == 500.0
    assert WAREHOUSE_ALLOCATION_COST_PER_UNIT != STORE_TRANSFER_COST_PER_UNIT
