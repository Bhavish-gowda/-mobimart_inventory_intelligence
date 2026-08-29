"""
Unit Tests for EOL Hold Economics Engine.
Tests deterministic hold calculations, future data isolation, and holding exposure.
"""

import pytest
from backend.engine.eol.hold import evaluate_hold_option


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
    }
    base.update(overrides)
    return base


class TestHoldCalculation:
    def test_hold_is_deterministic(self):
        """Same inputs must always produce the same hold economics output."""
        product = eol_product()
        opt1 = evaluate_hold_option(product=product, inventory_units=20, forecast_weekly_demand=2.0, current_week=24)
        opt2 = evaluate_hold_option(product=product, inventory_units=20, forecast_weekly_demand=2.0, current_week=24)

        assert opt1.net_financial_loss == pytest.approx(opt2.net_financial_loss)
        assert opt1.expected_recovery == pytest.approx(opt2.expected_recovery)

    def test_zero_inventory_returns_zero_exposure(self):
        """Zero inventory should result in zero holding exposure."""
        opt = evaluate_hold_option(product=eol_product(), inventory_units=0, forecast_weekly_demand=2.0, current_week=24)
        assert opt.net_financial_loss == pytest.approx(0.0)
        assert opt.units_affected == 0

    def test_high_eol_exposure_increases_hold_loss(self):
        """Higher inventory with EOL/declining products increases hold loss."""
        opt_high = evaluate_hold_option(product=eol_product(), inventory_units=50, forecast_weekly_demand=1.0, current_week=24)
        opt_low = evaluate_hold_option(product=eol_product(), inventory_units=5, forecast_weekly_demand=1.0, current_week=24)
        assert opt_high.net_financial_loss > opt_low.net_financial_loss

    def test_higher_demand_reduces_hold_loss(self):
        """Higher demand during holding period means more units sold, less unsold markdown."""
        opt_high_demand = evaluate_hold_option(product=eol_product(), inventory_units=10, forecast_weekly_demand=5.0, current_week=24)
        opt_low_demand = evaluate_hold_option(product=eol_product(), inventory_units=10, forecast_weekly_demand=0.5, current_week=24)
        assert opt_low_demand.net_financial_loss > opt_high_demand.net_financial_loss

    def test_future_actual_sales_not_used(self):
        """Hold evaluation must not take actual future sales as input — only forecast_weekly_demand."""
        # This test verifies the interface signature has no future_sales parameter
        import inspect
        from backend.engine.eol import hold as hold_mod
        sig = inspect.signature(hold_mod.evaluate_hold_option)
        param_names = list(sig.parameters.keys())
        # Should NOT have parameters for future_sales, actual_sales, or similar
        forbidden = {"future_sales", "actual_sales", "actual_units_sold", "future_demand_actual"}
        assert not forbidden.intersection(set(param_names)), (
            f"Hold function should not accept future actual data. Found: {forbidden.intersection(set(param_names))}"
        )

    def test_hold_option_correct_action_label(self):
        opt = evaluate_hold_option(product=eol_product(), inventory_units=10, forecast_weekly_demand=2.0, current_week=24)
        assert opt.action == "HOLD"

    def test_assumptions_populated(self):
        opt = evaluate_hold_option(product=eol_product(), inventory_units=10, forecast_weekly_demand=2.0, current_week=24)
        assert "remaining_weeks" in opt.assumptions
        assert "unsold_units" in opt.assumptions
        assert "terminal_markdown_pct" in opt.assumptions

    def test_no_successor_defaults_to_short_holding_period(self):
        """Without a successor, default hold period should be minimal for EOL products."""
        product = eol_product(successor_product_id=None, expected_successor_week=None, lifecycle_stage="EOL")
        opt = evaluate_hold_option(product=product, inventory_units=20, forecast_weekly_demand=1.0, current_week=24)
        assert opt.assumptions["remaining_weeks"] <= 4.0
