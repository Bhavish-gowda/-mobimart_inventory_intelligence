"""
Leakage Test: Verifies 100% immunity against future data leakage.
"""

import pandas as pd
import pytest

from backend.engine.simulation.models import SimulationConfig
from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
)
from backend.engine.simulation.runner import run_simulation

def test_future_demand_perturbation_does_not_affect_past_decisions():
    stores = [
        {"id": "STORE_01", "name": "Bangalore Main", "city": "Bangalore", "income_index": 1.5, "budget_affinity": 1.0, "flagship_affinity": 1.0},
    ]
    products = [
        {"id": "PROD_001", "model_name": "Nova 1", "segment": "Budget", "cost_price": 5000.0, "retail_price": 6500.0, "lifecycle_stage": "Peak"},
    ]
    inventory_records = [
        {"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 10, "weeks_of_cover": 2.0},
    ]

    # Generate 10 weeks of sales history
    sales_normal = []
    for wk in range(1, 11):
        sales_normal.append({
            "week_number": wk, "store_id": "STORE_01", "product_id": "PROD_001",
            "demand_units": 5, "units_sold": 5, "lost_sales_estimated": 0, "stockout_flag": False
        })
    df_normal = pd.DataFrame(sales_normal)

    # Modified future dataset: weeks 6..10 demand multiplied by 100x!
    sales_perturbed = []
    for row in sales_normal:
        r = dict(row)
        if r["week_number"] >= 6:
            r["demand_units"] = 500
            r["units_sold"] = 500
        sales_perturbed.append(r)
    df_perturbed = pd.DataFrame(sales_perturbed)

    config = SimulationConfig(start_week=1, end_week=5)  # Simulate weeks 1..5

    snapshot1 = build_starting_inventory_snapshot(inventory_records, products, stores, 1000000.0)
    snapshot2 = build_starting_inventory_snapshot(inventory_records, products, stores, 1000000.0)

    wh1 = build_warehouse_opening_state(products, df_normal, 4.0)
    wh2 = build_warehouse_opening_state(products, df_normal, 4.0)

    res_normal = run_simulation("MOBIMART", df_normal, stores, products, snapshot1, wh1, config)
    res_perturbed = run_simulation("MOBIMART", df_perturbed, stores, products, snapshot2, wh2, config)

    # Week 1..5 results MUST be 100% identical despite extreme future demand perturbation!
    for w_idx in range(5):
        w_norm = res_normal.weekly_results[w_idx]
        w_pert = res_perturbed.weekly_results[w_idx]

        assert w_norm.units_allocated == w_pert.units_allocated
        assert w_norm.fulfilled_units == w_pert.fulfilled_units
        assert w_norm.ending_store_units == w_pert.ending_store_units
        assert w_norm.revenue == w_pert.revenue
