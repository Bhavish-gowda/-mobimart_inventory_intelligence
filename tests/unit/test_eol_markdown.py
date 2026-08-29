"""
Unit Tests for EOL Markdown Economics Engine.
Tests markdown loss calculations, recovery values, and edge cases.
"""

import pytest
from backend.engine.eol.markdown import evaluate_markdown_option


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


class TestMarkdownCalculation:
    def test_markdown_loss_formula_correct(self):
        """Markdown loss = inventory_units * cost_price * markdown_pct."""
        product = eol_product(cost_price=10000.0, retail_price=12000.0, markdown_percentage=0.20)
        opt = evaluate_markdown_option(product=product, inventory_units=10)

        expected_loss = 10 * 10000.0 * 0.20  # = 20000.0
        assert opt.net_financial_loss == pytest.approx(expected_loss, rel=0.01)
        assert opt.action == "MARKDOWN"

    def test_markdown_recovery_formula_correct(self):
        """Expected recovery = inventory_units * retail_price * (1 - markdown_pct)."""
        product = eol_product(cost_price=10000.0, retail_price=12000.0, markdown_percentage=0.25)
        opt = evaluate_markdown_option(product=product, inventory_units=8)

        expected_recovery = 8 * 12000.0 * (1 - 0.25)  # = 72000.0
        assert opt.expected_recovery == pytest.approx(expected_recovery, rel=0.01)

    def test_higher_markdown_pct_increases_expected_loss(self):
        """Higher markdown percentage should increase expected loss."""
        product_high = eol_product(markdown_percentage=0.40)
        product_low = eol_product(markdown_percentage=0.10)

        opt_high = evaluate_markdown_option(product=product_high, inventory_units=15)
        opt_low = evaluate_markdown_option(product=product_low, inventory_units=15)

        assert opt_high.net_financial_loss > opt_low.net_financial_loss

    def test_custom_markdown_pct_overrides_product_pct(self):
        """Custom markdown_pct param should override product's markdown_percentage field."""
        product = eol_product(cost_price=5000.0, markdown_percentage=0.28)
        opt = evaluate_markdown_option(product=product, inventory_units=10, custom_markdown_pct=0.10)

        expected = 10 * 5000.0 * 0.10
        assert opt.net_financial_loss == pytest.approx(expected, rel=0.01)

    def test_zero_units_returns_zero_loss(self):
        """Zero inventory creates zero markdown exposure."""
        product = eol_product()
        opt = evaluate_markdown_option(product=product, inventory_units=0)

        assert opt.net_financial_loss == pytest.approx(0.0)
        assert opt.expected_recovery == pytest.approx(0.0)
        assert opt.units_affected == 0

    def test_assumptions_populated(self):
        """Assumptions dict should contain key financial breakdowns."""
        product = eol_product()
        opt = evaluate_markdown_option(product=product, inventory_units=10)

        assert "markdown_pct" in opt.assumptions
        assert "cost_price" in opt.assumptions
        assert "retail_price" in opt.assumptions
        assert "markdown_cost_loss" in opt.assumptions

    def test_explanation_contains_rupee_amounts(self):
        """Explanation text should reference rupee amounts from calculation."""
        product = eol_product(cost_price=8000.0, retail_price=10000.0, markdown_percentage=0.20)
        opt = evaluate_markdown_option(product=product, inventory_units=5)

        assert "₹" in opt.explanation
        # Loss = 5 * 8000 * 0.20 = 8000.0
        assert "8,000" in opt.explanation or "8000" in opt.explanation
