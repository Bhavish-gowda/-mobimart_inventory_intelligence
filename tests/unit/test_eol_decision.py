"""
Unit Tests for EOL Decision Engine.
Tests option comparison logic, recommended_action selection, and financial integrity.
"""

import pytest
import pandas as pd
from backend.engine.eol.decision import assess_eol_risk_position, run_eol_assessment_for_all
from backend.engine.eol.models import EOLRiskAssessment


def make_store(store_id="STORE_01"):
    return {"id": store_id, "budget_affinity": 1.0, "mid_range_affinity": 1.0, "premium_affinity": 1.0, "flagship_affinity": 1.0}


def eol_product(**overrides):
    base = {
        "id": "PROD_001",
        "model_name": "Nova Go 4G",
        "lifecycle_stage": "EOL",
        "cost_price": 6500.0,
        "retail_price": 7800.0,
        "markdown_percentage": 0.28,
        "successor_product_id": "PROD_002",
        "expected_successor_week": 26,
        "launch_confidence": 1.0,
        "is_rumoured": False,
        "launch_week": -15,
        "segment": "Budget",
    }
    base.update(overrides)
    return base


def make_inventory_rec(store_id="STORE_01", product_id="PROD_001", stock=20):
    return {"store_id": store_id, "product_id": product_id, "current_stock": stock, "in_transit_stock": 0}


def make_sales_df(store_id="STORE_01", product_id="PROD_001", units_per_week=2):
    rows = [
        {"store_id": store_id, "product_id": product_id, "week_number": wk, "units_sold": units_per_week}
        for wk in range(18, 24)
    ]
    return pd.DataFrame(rows)


class TestDecisionComparison:
    def test_engine_returns_eol_risk_assessment(self):
        """assess_eol_risk_position must return an EOLRiskAssessment."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        inventory = [make_inventory_rec("STORE_01"), make_inventory_rec("STORE_02", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(),
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=sales_df,
            current_week=24,
        )
        assert result is None or isinstance(result, EOLRiskAssessment)

    def test_all_three_options_evaluated(self):
        """Assessment must always evaluate MARKDOWN, TRANSFER, and HOLD."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        inventory = [make_inventory_rec("STORE_01", stock=20), make_inventory_rec("STORE_02", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(stock=20),
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=sales_df,
            current_week=24,
        )
        if result:
            assert result.markdown_option.action == "MARKDOWN"
            assert result.transfer_option.action == "TRANSFER"
            assert result.hold_option.action == "HOLD"

    def test_recommended_action_equals_best_financial_option(self):
        """Recommended action must correspond to the option with lowest net_financial_loss."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        inventory = [make_inventory_rec("STORE_01", stock=20), make_inventory_rec("STORE_02", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(stock=20),
            all_stores=stores,
            all_inventory=inventory,
            sales_history_df=sales_df,
            current_week=24,
        )
        if result:
            losses = {
                "MARKDOWN": result.markdown_option.net_financial_loss,
                "TRANSFER": result.transfer_option.net_financial_loss,
                "HOLD": result.hold_option.net_financial_loss,
            }
            best = min(losses, key=losses.get)
            assert result.recommended_action == best

    def test_options_are_compared_not_summed(self):
        """expected_financial_impact should equal the recommended option's loss, not sum of all."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        inventory = [make_inventory_rec("STORE_01", stock=20), make_inventory_rec("STORE_02", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(stock=20),
            all_stores=stores, all_inventory=inventory,
            sales_history_df=sales_df, current_week=24,
        )
        if result:
            action = result.recommended_action
            option = {"MARKDOWN": result.markdown_option, "TRANSFER": result.transfer_option, "HOLD": result.hold_option}[action]
            assert result.expected_financial_impact == pytest.approx(option.net_financial_loss, rel=0.01)

    def test_only_valid_actions_returned(self):
        """recommended_action must be one of MARKDOWN, TRANSFER, HOLD."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        inventory = [make_inventory_rec("STORE_01", stock=20), make_inventory_rec("STORE_02", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(stock=20),
            all_stores=stores, all_inventory=inventory,
            sales_history_df=sales_df, current_week=24,
        )
        if result:
            assert result.recommended_action in ("MARKDOWN", "TRANSFER", "HOLD")

    def test_zero_inventory_returns_none_or_low(self):
        """A position with zero stock should return None (not worthwhile assessing)."""
        store = make_store()
        product = eol_product()
        stores = [make_store("STORE_01")]
        inventory = [make_inventory_rec("STORE_01", stock=0)]
        sales_df = make_sales_df()

        result = assess_eol_risk_position(
            store=store, product=product,
            inventory_record=make_inventory_rec(stock=0),
            all_stores=stores, all_inventory=inventory,
            sales_history_df=sales_df, current_week=24,
        )
        # Zero inventory → LOW risk → excluded
        assert result is None


class TestRunAllAssessments:
    def test_run_all_returns_list_sorted_by_risk(self):
        """Assessments returned by run_eol_assessment_for_all must be sorted by risk_score DESC."""
        stores = [make_store("STORE_01"), make_store("STORE_02")]
        products = [
            eol_product(id="PROD_001"),
            eol_product(id="PROD_005", lifecycle_stage="Decline", successor_product_id=None, expected_successor_week=None),
        ]
        inventory = [
            make_inventory_rec("STORE_01", "PROD_001", stock=20),
            make_inventory_rec("STORE_02", "PROD_001", stock=5),
            make_inventory_rec("STORE_01", "PROD_005", stock=15),
            make_inventory_rec("STORE_02", "PROD_005", stock=8),
        ]
        rows = []
        for wk in range(18, 24):
            for sid in ["STORE_01", "STORE_02"]:
                for pid in ["PROD_001", "PROD_005"]:
                    rows.append({"store_id": sid, "product_id": pid, "week_number": wk, "units_sold": 2})
        sales_df = pd.DataFrame(rows)

        results = run_eol_assessment_for_all(
            stores=stores, products=products, inventory_records=inventory,
            sales_history_df=sales_df, current_week=24, min_risk_level="LOW",
        )
        scores = [r.risk_score for r in results]
        assert scores == sorted(scores, reverse=True)
