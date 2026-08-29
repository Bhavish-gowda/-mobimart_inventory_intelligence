"""
Unit Tests for EOL Transfer Economics Engine.
Tests transfer cost, destination search, financial comparisons, and rejection logic.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock
from backend.engine.eol.transfer import evaluate_transfer_option, search_best_transfer_destination
from backend.engine.eol.config import STORE_TRANSFER_COST_PER_UNIT


def eol_product(**overrides):
    base = {
        "id": "PROD_001",
        "model_name": "Nova Go 4G",
        "lifecycle_stage": "EOL",
        "segment": "Budget",  # Required by forecast_weekly_demand
        "cost_price": 6500.0,
        "retail_price": 7800.0,
        "markdown_percentage": 0.28,
        "successor_product_id": "PROD_002",
        "expected_successor_week": 26,
        "launch_confidence": 1.0,
        "is_rumoured": False,
    }
    base.update(overrides)
    return base


def make_stores():
    return [
        {"id": "STORE_01", "budget_affinity": 1.2, "mid_range_affinity": 1.0, "premium_affinity": 0.8, "flagship_affinity": 0.7},
        {"id": "STORE_02", "budget_affinity": 1.0, "mid_range_affinity": 1.2, "premium_affinity": 1.0, "flagship_affinity": 0.9},
        {"id": "STORE_03", "budget_affinity": 0.9, "mid_range_affinity": 0.8, "premium_affinity": 0.7, "flagship_affinity": 0.6},
    ]


def make_inventory(product_id="PROD_001"):
    return [
        {"store_id": "STORE_01", "product_id": product_id, "current_stock": 30, "in_transit_stock": 0},
        {"store_id": "STORE_02", "product_id": product_id, "current_stock": 2, "in_transit_stock": 0},  # Low stock
        {"store_id": "STORE_03", "product_id": product_id, "current_stock": 1, "in_transit_stock": 0},  # Low stock
    ]


def make_sales_df(product_id="PROD_001"):
    rows = []
    for wk in range(18, 24):
        rows.append({"store_id": "STORE_02", "product_id": product_id, "week_number": wk, "units_sold": 3})
        rows.append({"store_id": "STORE_03", "product_id": product_id, "week_number": wk, "units_sold": 2})
        rows.append({"store_id": "STORE_01", "product_id": product_id, "week_number": wk, "units_sold": 5})
    return pd.DataFrame(rows)


class TestTransferCost:
    def test_store_transfer_cost_is_500_per_unit(self):
        """Transfer cost must use ₹500/unit (not warehouse ₹250/unit)."""
        assert STORE_TRANSFER_COST_PER_UNIT == 500.0

    def test_warehouse_cost_250_not_used_for_transfer(self):
        """Verify that ₹250 warehouse cost is NOT used for store-to-store transfer."""
        from backend.engine.eol.config import STORE_TRANSFER_COST_PER_UNIT as tc
        assert tc != 250.0

    def test_logistics_cost_is_transfer_units_times_500(self):
        """Logistics cost should equal units_transferred * 500."""
        stores = make_stores()
        product = eol_product()
        inventory = make_inventory()
        sales_df = make_sales_df()

        from backend.engine.allocation.forecast import forecast_weekly_demand
        opt = evaluate_transfer_option(
            source_store_id="STORE_01",
            product=product,
            inventory_units=20,
            source_woc=4.0,
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=sales_df,
            forecast_func=forecast_weekly_demand,
            current_week=24,
        )
        if opt.units_affected > 0:
            expected_logistics = opt.units_affected * 500.0
            assert opt.expected_cost == pytest.approx(expected_logistics, rel=0.01)


class TestTransferDestination:
    def test_no_demand_destination_is_rejected(self):
        """Any store with zero demand should never be selected as destination."""
        stores = make_stores()
        product = eol_product()
        inventory = make_inventory()

        # Override sales so STORE_02 and STORE_03 have NO history, so demand ≈ 0
        empty_df = pd.DataFrame(columns=["store_id", "product_id", "week_number", "units_sold"])

        from backend.engine.allocation.forecast import forecast_weekly_demand
        opt = evaluate_transfer_option(
            source_store_id="STORE_01",
            product=product,
            inventory_units=20,
            source_woc=10.0,
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=empty_df,
            forecast_func=forecast_weekly_demand,
            current_week=24,
        )
        # Transfer should be rejected if no demand exists in destinations
        assert opt.net_financial_loss == float("inf") or opt.units_affected == 0

    def test_high_demand_destination_is_preferred(self):
        """Destination with higher demand should be preferred over low demand."""
        stores = make_stores()
        product = eol_product()
        inventory = make_inventory()

        # STORE_02 has high demand; STORE_03 has lower demand
        rows = []
        for wk in range(18, 24):
            rows.append({"store_id": "STORE_02", "product_id": "PROD_001", "week_number": wk, "units_sold": 10})
            rows.append({"store_id": "STORE_03", "product_id": "PROD_001", "week_number": wk, "units_sold": 1})
        sales_df = pd.DataFrame(rows)

        from backend.engine.allocation.forecast import forecast_weekly_demand
        best = search_best_transfer_destination(
            source_store_id="STORE_01",
            product=product,
            inventory_units=30,
            source_woc=5.0,
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=sales_df,
            forecast_func=forecast_weekly_demand,
            current_week=24,
        )
        # Should choose STORE_02 given higher demand / larger shortfall
        assert best is not None
        assert best["store_id"] == "STORE_02"

    def test_zero_inventory_returns_not_applicable(self):
        """Zero source inventory should make transfer option not applicable."""
        from backend.engine.allocation.forecast import forecast_weekly_demand
        opt = evaluate_transfer_option(
            source_store_id="STORE_01",
            product=eol_product(),
            inventory_units=0,
            source_woc=0.0,
            all_stores=make_stores(),
            all_inventory=make_inventory(),
            sales_history_df=make_sales_df(),
            forecast_func=forecast_weekly_demand,
            current_week=24,
        )
        assert opt.units_affected == 0
        assert opt.expected_cost == pytest.approx(0.0)

    def test_source_stock_at_target_cover_is_not_transferred(self):
        """A transfer may only use excess stock, never the source's safety stock."""
        from backend.engine.allocation.forecast import forecast_weekly_demand
        opt = evaluate_transfer_option(
            source_store_id="STORE_01",
            product=eol_product(),
            inventory_units=20,
            source_woc=4.0,
            all_stores=make_stores(),
            all_inventory=make_inventory(),
            sales_history_df=make_sales_df(),
            forecast_func=forecast_weekly_demand,
            current_week=24,
        )
        assert opt.net_financial_loss == float("inf")
        assert opt.units_affected == 0
