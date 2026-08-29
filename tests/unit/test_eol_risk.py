"""
Unit Tests for EOL Risk Scoring Engine.
Tests lifecycle stage risk, successor proximity/confidence, weeks-of-cover excess,
demand decline contributions, and final risk level thresholds.
"""

import pytest
from backend.engine.eol.risk import calculate_eol_risk_score, calculate_weeks_of_cover


# ─── Fixtures ────────────────────────────────────────────────────────────────

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

def peak_product(**overrides):
    base = {
        "id": "PROD_010",
        "model_name": "Apex Peak Pro",
        "lifecycle_stage": "Peak",
        "cost_price": 20000.0,
        "retail_price": 25000.0,
        "markdown_percentage": 0.00,
        "successor_product_id": None,
        "expected_successor_week": None,
        "launch_confidence": 1.0,
        "is_rumoured": False,
    }
    base.update(overrides)
    return base


# ─── Risk Scoring Tests ───────────────────────────────────────────────────────

class TestRiskScoreLifecycle:
    def test_eol_product_has_higher_risk_than_peak_product(self):
        """EOL product should always score higher than an equivalent Peak product."""
        score_eol, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=20,
            forecast_weekly_demand=2.0,
            recent_sales_velocity=1.5,
            rolling_avg=2.0,
            current_week=24,
        )
        score_peak, _, _, _ = calculate_eol_risk_score(
            product=peak_product(),
            inventory_units=20,
            forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0,
            rolling_avg=2.0,
            current_week=24,
        )
        assert score_eol > score_peak, f"EOL risk ({score_eol}) should exceed Peak risk ({score_peak})"

    def test_decline_product_risk_between_eol_and_peak(self):
        """Decline product should score between EOL and Peak."""
        score_eol, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=10, forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        score_decline, _, _, _ = calculate_eol_risk_score(
            product=eol_product(lifecycle_stage="Decline", successor_product_id=None, expected_successor_week=None),
            inventory_units=10, forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        score_peak, _, _, _ = calculate_eol_risk_score(
            product=peak_product(),
            inventory_units=10, forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        assert score_eol > score_decline >= score_peak


class TestRiskScoreSuccessor:
    def test_imminent_confirmed_successor_increases_risk(self):
        """A successor launching in 2 weeks should significantly raise risk."""
        score_imm, _, _, _ = calculate_eol_risk_score(
            product=eol_product(expected_successor_week=26),  # 2 weeks from w24
            inventory_units=15, forecast_weekly_demand=1.5,
            recent_sales_velocity=1.5, rolling_avg=1.5, current_week=24,
        )
        score_none, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=15, forecast_weekly_demand=1.5,
            recent_sales_velocity=1.5, rolling_avg=1.5, current_week=24,
        )
        assert score_imm > score_none

    def test_confirmed_successor_has_greater_risk_than_rumoured(self):
        """Confirmed successor should give higher risk score than rumoured successor."""
        score_confirmed, _, _, _ = calculate_eol_risk_score(
            product=eol_product(
                expected_successor_week=26, launch_confidence=1.0, is_rumoured=False
            ),
            inventory_units=20, forecast_weekly_demand=1.5,
            recent_sales_velocity=1.5, rolling_avg=1.5, current_week=24,
        )
        score_rumoured, _, _, _ = calculate_eol_risk_score(
            product=eol_product(
                expected_successor_week=26, launch_confidence=0.65, is_rumoured=True
            ),
            inventory_units=20, forecast_weekly_demand=1.5,
            recent_sales_velocity=1.5, rolling_avg=1.5, current_week=24,
        )
        assert score_confirmed > score_rumoured, (
            f"Confirmed risk ({score_confirmed}) should exceed rumoured ({score_rumoured})"
        )

    def test_far_successor_lower_risk_than_imminent(self):
        score_far, _, _, _ = calculate_eol_risk_score(
            product=eol_product(expected_successor_week=40),  # 16 weeks away
            inventory_units=15, forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        score_imm, _, _, _ = calculate_eol_risk_score(
            product=eol_product(expected_successor_week=26),  # 2 weeks away
            inventory_units=15, forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        assert score_imm > score_far


class TestRiskScoreInventoryExcess:
    def test_high_weeks_of_cover_increases_risk(self):
        """Same product with high WOC should score higher than low WOC."""
        score_high, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=50,  # high: 25 WOC
            forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        score_low, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=5,  # low: 2.5 WOC
            forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        assert score_high > score_low

    def test_zero_demand_causes_max_excess_score(self):
        """Zero demand with positive inventory should push excess score up."""
        score, risk_level, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=20,
            forecast_weekly_demand=0.0,
            recent_sales_velocity=0.0, rolling_avg=0.0, current_week=24,
        )
        assert risk_level in ("HIGH", "CRITICAL")


class TestRiskScoreDemandDecline:
    def test_declining_demand_increases_risk(self):
        """Declining velocity below rolling avg should increase risk score."""
        score_declining, _, factors, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=15,
            forecast_weekly_demand=1.0,
            recent_sales_velocity=0.5,  # Declining
            rolling_avg=2.0,
            current_week=24,
        )
        score_stable, _, _, _ = calculate_eol_risk_score(
            product=eol_product(successor_product_id=None, expected_successor_week=None),
            inventory_units=15,
            forecast_weekly_demand=1.0,
            recent_sales_velocity=2.0,  # Stable
            rolling_avg=2.0,
            current_week=24,
        )
        assert score_declining > score_stable


class TestRiskLevels:
    def test_risk_levels_mapped_correctly(self):
        """Risk levels must be one of LOW/MEDIUM/HIGH/CRITICAL."""
        _, risk_level, _, _ = calculate_eol_risk_score(
            product=peak_product(),
            inventory_units=5, forecast_weekly_demand=5.0,
            recent_sales_velocity=5.0, rolling_avg=5.0, current_week=24,
        )
        assert risk_level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_zero_inventory_always_low(self):
        """Zero inventory should return LOW risk."""
        _, risk_level, _, _ = calculate_eol_risk_score(
            product=eol_product(),
            inventory_units=0,
            forecast_weekly_demand=2.0,
            recent_sales_velocity=2.0, rolling_avg=2.0, current_week=24,
        )
        assert risk_level == "LOW"

    def test_score_bounded_0_100(self):
        """Risk score should never exceed 100 or go below 0."""
        score, _, _, _ = calculate_eol_risk_score(
            product=eol_product(expected_successor_week=25, launch_confidence=1.0, is_rumoured=False),
            inventory_units=500, forecast_weekly_demand=0.001,
            recent_sales_velocity=0.001, rolling_avg=5.0, current_week=24,
        )
        assert 0.0 <= score <= 100.0


class TestWeeksOfCoverHelper:
    def test_standard_woc(self):
        assert calculate_weeks_of_cover(20, 4.0) == pytest.approx(5.0)

    def test_zero_demand_returns_99(self):
        assert calculate_weeks_of_cover(10, 0.0) == pytest.approx(99.0)

    def test_zero_inventory_zero_demand_returns_zero(self):
        assert calculate_weeks_of_cover(0, 0.0) == pytest.approx(0.0)
