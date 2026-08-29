"""
Unit tests for Inventory Operations & Inventory Conservation Accounting.
"""

import pandas as pd
import pytest

from backend.engine.simulation.inventory import (
    apply_eol_transfers,
    apply_eol_markdowns,
    fulfill_weekly_demand,
    verify_inventory_conservation,
)
from backend.engine.eol.models import PortfolioTransferResolution, EOLTransferRoute

def test_verify_inventory_conservation_success():
    assert verify_inventory_conservation(
        starting_store_units=100,
        allocated_units=20,
        fulfilled_units=30,
        ending_store_units=90,
    )

def test_verify_inventory_conservation_failure_raises_error():
    with pytest.raises(ValueError):
        verify_inventory_conservation(
            starting_store_units=100,
            allocated_units=20,
            fulfilled_units=30,
            ending_store_units=85,  # Mismatch! Should be 90
        )

def test_apply_eol_transfers_updates_store_stocks():
    store_inventory = {
        ("STORE_A", "PROD_001"): {"store_id": "STORE_A", "product_id": "PROD_001", "current_stock": 20},
        ("STORE_B", "PROD_001"): {"store_id": "STORE_B", "product_id": "PROD_001", "current_stock": 5},
    }
    route = EOLTransferRoute(
        source_store_id="STORE_A",
        destination_store_id="STORE_B",
        product_id="PROD_001",
        requested_units=10,
        source_excess_units=15,
        destination_shortfall_units=10,
        expected_cost=5000.0,
        expected_loss=1000.0,
        savings_vs_hold=2000.0,
        status="APPROVED",
        approved_units=10,
    )
    resolution = PortfolioTransferResolution(
        approved_routes=[route],
        rejected_routes=[],
        candidate_transfer_opportunity=2000.0,
        approved_transfer_opportunity=2000.0,
        source_capacity_ledger={},
        destination_capacity_ledger={},
    )

    units, cost = apply_eol_transfers(store_inventory, resolution, transfer_cost_per_unit=500.0)

    assert units == 10
    assert cost == 5000.0
    assert store_inventory[("STORE_A", "PROD_001")]["current_stock"] == 10
    assert store_inventory[("STORE_B", "PROD_001")]["current_stock"] == 15

def test_fulfill_weekly_demand_updates_stock_and_metrics():
    store_inventory = {
        ("STORE_A", "PROD_001"): {"store_id": "STORE_A", "product_id": "PROD_001", "current_stock": 10},
    }
    week_sales_df = pd.DataFrame([
        {"store_id": "STORE_A", "product_id": "PROD_001", "demand_units": 15, "units_sold": 10}
    ])
    products_by_id = {
        "PROD_001": {"cost_price": 5000.0, "retail_price": 7000.0}
    }

    res = fulfill_weekly_demand(store_inventory, week_sales_df, products_by_id)

    assert res["demand_units"] == 15
    assert res["fulfilled_units"] == 10
    assert res["lost_sales_units"] == 5
    assert res["lost_sales_value"] == 35000.0  # 5 * 7000
    assert res["revenue"] == 70000.0  # 10 * 7000
    assert res["cogs"] == 50000.0     # 10 * 5000
    assert res["gross_margin"] == 20000.0
    assert store_inventory[("STORE_A", "PROD_001")]["current_stock"] == 0
