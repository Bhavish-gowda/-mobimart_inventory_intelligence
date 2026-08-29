"""
Unit Tests for EOL Explanation Engine.
Tests that generated explanations are accurate, reference correct rupee amounts,
match recommended actions, and contain proper product/store identifiers.
"""

import pytest
from backend.engine.eol.models import EOLActionOption
from backend.engine.eol.explanations import generate_eol_explanation


def make_option(action, expected_cost, expected_recovery, net_loss, units=10, target=None):
    return EOLActionOption(
        action=action,
        expected_cost=expected_cost,
        expected_recovery=expected_recovery,
        net_financial_loss=net_loss,
        units_affected=units,
        target_store_id=target,
        assumptions={},
        explanation=f"{action} option explanation.",
    )


class TestExplanationContent:
    def test_explanation_contains_product_id(self):
        """Explanation must include the product ID."""
        md_opt = make_option("MARKDOWN", 0.0, 15000.0, 5000.0)
        tr_opt = make_option("TRANSFER", 5000.0, 11000.0, 7000.0, target="STORE_05")
        hd_opt = make_option("HOLD", 1000.0, 10000.0, 9000.0)

        result = generate_eol_explanation(
            risk_level="HIGH", risk_score=72.0,
            store_id="STORE_01", product_name="Nova Go 4G", product_id="PROD_001",
            inventory_units=15, weeks_of_cover=7.5,
            successor_id="PROD_002", weeks_to_successor=4.0,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="MARKDOWN",
        )
        assert "PROD_001" in result

    def test_explanation_contains_recommended_action(self):
        """Explanation must mention the recommended action."""
        md_opt = make_option("MARKDOWN", 0.0, 14000.0, 4000.0)
        tr_opt = make_option("TRANSFER", 6000.0, 10000.0, 8000.0, target="STORE_02")
        hd_opt = make_option("HOLD", 2000.0, 8000.0, 12000.0)

        result = generate_eol_explanation(
            risk_level="CRITICAL", risk_score=85.0,
            store_id="STORE_01", product_name="Nova Go 4G", product_id="PROD_001",
            inventory_units=20, weeks_of_cover=10.0,
            successor_id="PROD_002", weeks_to_successor=2.0,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="MARKDOWN",
        )
        assert "MARKDOWN" in result

    def test_transfer_explanation_contains_destination(self):
        """Transfer recommendation must mention target store ID."""
        md_opt = make_option("MARKDOWN", 0.0, 10000.0, 9000.0)
        tr_opt = make_option("TRANSFER", 5000.0, 12000.0, 5500.0, units=10, target="STORE_07")
        hd_opt = make_option("HOLD", 2000.0, 9000.0, 14000.0)

        result = generate_eol_explanation(
            risk_level="CRITICAL", risk_score=88.0,
            store_id="STORE_01", product_name="Apex Lite 10", product_id="PROD_003",
            inventory_units=20, weeks_of_cover=9.8,
            successor_id="PROD_004", weeks_to_successor=2.0,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="TRANSFER",
        )
        assert "STORE_07" in result

    def test_transfer_explanation_contains_transfer_cost(self):
        """Transfer explanation must include the rupee transfer cost."""
        md_opt = make_option("MARKDOWN", 0.0, 10000.0, 9000.0)
        tr_opt = make_option("TRANSFER", 10000.0, 12000.0, 5000.0, units=20, target="STORE_07")
        hd_opt = make_option("HOLD", 2000.0, 9000.0, 14000.0)

        result = generate_eol_explanation(
            risk_level="CRITICAL", risk_score=90.0,
            store_id="STORE_01", product_name="Some Phone", product_id="PROD_054",
            inventory_units=20, weeks_of_cover=9.8,
            successor_id="PROD_055", weeks_to_successor=2.0,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="TRANSFER",
        )
        assert "₹" in result
        assert "10,000" in result or "10000" in result

    def test_numbers_in_explanation_match_inputs(self):
        """Hold loss must appear in explanation when HOLD is recommended."""
        md_opt = make_option("MARKDOWN", 0.0, 10000.0, 22000.0)
        tr_opt = make_option("TRANSFER", 0.0, 0.0, float("inf"))
        hd_opt = make_option("HOLD", 1500.0, 7000.0, 3500.0)

        result = generate_eol_explanation(
            risk_level="MEDIUM", risk_score=45.0,
            store_id="STORE_02", product_name="Zenith C1", product_id="PROD_008",
            inventory_units=5, weeks_of_cover=2.5,
            successor_id=None, weeks_to_successor=None,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="HOLD",
        )
        # Hold loss 3500 should be in the explanation
        assert "3,500" in result or "3500" in result

    def test_risk_level_appears_in_header(self):
        """Risk level must appear at the start of the explanation."""
        md_opt = make_option("MARKDOWN", 0.0, 10000.0, 5000.0)
        tr_opt = make_option("TRANSFER", 0.0, 0.0, float("inf"))
        hd_opt = make_option("HOLD", 1500.0, 7000.0, 8000.0)

        result = generate_eol_explanation(
            risk_level="HIGH", risk_score=65.0,
            store_id="STORE_03", product_name="Test Phone", product_id="PROD_010",
            inventory_units=12, weeks_of_cover=6.0,
            successor_id=None, weeks_to_successor=None,
            risk_factors=[], markdown_opt=md_opt, transfer_opt=tr_opt, hold_opt=hd_opt,
            recommended_action="MARKDOWN",
        )
        assert result.startswith("HIGH")
