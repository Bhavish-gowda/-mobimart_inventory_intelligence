"""
End-to-end Unit tests for 52-Week Rolling Simulation Runner.
"""

import pandas as pd
import pytest

from backend.engine.simulation.models import SimulationConfig
from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
)
from backend.engine.simulation.runner import run_simulation

@pytest.fixture
def mock_dataset():
    stores = [
        {"id": "STORE_01", "name": "Bangalore Flagship", "city": "Bangalore", "income_index": 1.5, "budget_affinity": 1.0, "flagship_affinity": 1.0},
        {"id": "STORE_02", "name": "Mysore Main", "city": "Mysore", "income_index": 1.0, "budget_affinity": 1.2, "flagship_affinity": 0.8},
    ]
    products = [
        {"id": "PROD_001", "model_name": "Nova 1", "segment": "Budget", "cost_price": 5000.0, "retail_price": 6500.0, "lifecycle_stage": "Peak"},
        {"id": "PROD_002", "model_name": "Nova 2", "segment": "Mid-Range", "cost_price": 12000.0, "retail_price": 16000.0, "lifecycle_stage": "EOL", "successor_product_id": "PROD_001", "expected_successor_week": 10},
    ]
    inventory_records = [
        {"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 20, "weeks_of_cover": 4.0},
        {"store_id": "STORE_01", "product_id": "PROD_002", "current_stock": 30, "weeks_of_cover": 8.0},
        {"store_id": "STORE_02", "product_id": "PROD_001", "current_stock": 15, "weeks_of_cover": 3.0},
        {"store_id": "STORE_02", "product_id": "PROD_002", "current_stock": 25, "weeks_of_cover": 7.0},
    ]
    
    sales_rows = []
    for wk in range(1, 13):
        for s in stores:
            for p in products:
                sales_rows.append({
                    "week_number": wk,
                    "store_id": s["id"],
                    "product_id": p["id"],
                    "demand_units": 5,
                    "units_sold": 5,
                    "lost_sales_estimated": 0,
                    "stockout_flag": False,
                })
    sales_df = pd.DataFrame(sales_rows)
    return stores, products, inventory_records, sales_df

def test_simulation_runner_baseline_and_mobimart_execution(mock_dataset):
    stores, products, inventory_records, sales_df = mock_dataset
    config = SimulationConfig(start_week=1, end_week=12, capital_budget_limit=40000000.0, starting_capital_target=1000000.0)

    snapshot = build_starting_inventory_snapshot(inventory_records, products, stores, config.starting_capital_target)
    wh_opening = build_warehouse_opening_state(products, sales_df, cover_weeks=4.0)

    # Run Baseline
    res_base = run_simulation("BASELINE", sales_df, stores, products, snapshot, wh_opening, config)
    assert len(res_base.weekly_results) == 12
    assert res_base.strategy_name == "BASELINE"
    assert res_base.total_fulfilled_units > 0

    # Run MobiMart
    res_mobi = run_simulation("MOBIMART", sales_df, stores, products, snapshot, wh_opening, config)
    assert len(res_mobi.weekly_results) == 12
    assert res_mobi.strategy_name == "MOBIMART"
    assert res_mobi.total_fulfilled_units > 0

def test_identical_starting_states_and_demand_streams(mock_dataset):
    stores, products, inventory_records, sales_df = mock_dataset
    config = SimulationConfig(start_week=1, end_week=6, capital_budget_limit=40000000.0)

    snapshot = build_starting_inventory_snapshot(inventory_records, products, stores, 1000000.0)
    wh_opening = build_warehouse_opening_state(products, sales_df, cover_weeks=4.0)

    res_base = run_simulation("BASELINE", sales_df, stores, products, snapshot, wh_opening, config)
    res_mobi = run_simulation("MOBIMART", sales_df, stores, products, snapshot, wh_opening, config)

    # Both must start from exact same snapshot and warehouse stock
    assert res_base.starting_snapshot.operational_inventory_cost == res_mobi.starting_snapshot.operational_inventory_cost
    assert sum(res_base.weekly_results[0].demand_units for r in [res_base]) == sum(res_mobi.weekly_results[0].demand_units for r in [res_mobi])
