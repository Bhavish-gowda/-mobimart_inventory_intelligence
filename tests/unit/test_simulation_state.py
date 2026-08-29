"""
Unit tests for Simulation State & Priority-Based Starting Inventory Construction.
"""

import pandas as pd
import pytest

from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
    get_independent_store_inventory,
)

def test_priority_based_starting_inventory_budget_compliance():
    stores = [{"id": "STORE_01", "name": "Bangalore Main"}]
    products = [
        {"id": "PROD_001", "cost_price": 10000.0, "lifecycle_stage": "Peak"},
        {"id": "PROD_002", "cost_price": 20000.0, "lifecycle_stage": "EOL"},
    ]
    # Raw inventory total: 3,000 units * 10,000 + 1,500 units * 20,000 = ₹6,00,00,000 (Exceeds ₹4 Cr)
    inventory_records = [
        {"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 3000, "weeks_of_cover": 10.0},
        {"store_id": "STORE_01", "product_id": "PROD_002", "current_stock": 1500, "weeks_of_cover": 8.0},
    ]

    snapshot = build_starting_inventory_snapshot(
        inventory_df_or_records=inventory_records,
        products=products,
        stores=stores,
        target_capital=38000000.0,  # ₹3.80 Cr target
    )

    assert snapshot.operational_inventory_cost <= 38000000.0
    assert snapshot.raw_inventory_cost == 60000000.0
    assert snapshot.capital_headroom >= 2000000.0
    assert snapshot.units_retained < snapshot.raw_total_units

def test_store_and_product_diversity_preserved():
    stores = [
        {"id": "STORE_01", "name": "Store 1"},
        {"id": "STORE_02", "name": "Store 2"},
    ]
    products = [
        {"id": "P1", "cost_price": 5000.0, "lifecycle_stage": "Peak"},
        {"id": "P2", "cost_price": 5000.0, "lifecycle_stage": "EOL"},
    ]
    inventory_records = [
        {"store_id": "STORE_01", "product_id": "P1", "current_stock": 500, "weeks_of_cover": 5.0},
        {"store_id": "STORE_01", "product_id": "P2", "current_stock": 500, "weeks_of_cover": 8.0},
        {"store_id": "STORE_02", "product_id": "P1", "current_stock": 500, "weeks_of_cover": 5.0},
        {"store_id": "STORE_02", "product_id": "P2", "current_stock": 500, "weeks_of_cover": 8.0},
    ]

    snapshot = build_starting_inventory_snapshot(
        inventory_df_or_records=inventory_records,
        products=products,
        stores=stores,
        target_capital=3800000.0,  # ₹38 Lakhs
    )

    # Verify every key has >= 1 stock retained
    for key, stock in snapshot.store_product_stock.items():
        assert stock >= 1

def test_state_copies_are_independent():
    stores = [{"id": "S1"}]
    products = [{"id": "P1", "cost_price": 1000.0, "lifecycle_stage": "Peak"}]
    inventory_records = [{"store_id": "S1", "product_id": "P1", "current_stock": 100, "weeks_of_cover": 4.0}]

    snapshot = build_starting_inventory_snapshot(inventory_records, products, stores, 38000000.0)

    copy1 = get_independent_store_inventory(snapshot)
    copy2 = get_independent_store_inventory(snapshot)

    # Mutate copy1
    copy1[("S1", "P1")]["current_stock"] -= 10

    # Assert copy2 remains unmutated
    assert copy2[("S1", "P1")]["current_stock"] == snapshot.store_product_stock["S1|P1"]
    assert copy1[("S1", "P1")]["current_stock"] != copy2[("S1", "P1")]["current_stock"]
