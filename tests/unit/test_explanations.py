"""
Pytest unit tests for Financial Explanation Engine.
Verifies structured explanation payload generation, reason code headlines,
and numerical narrative formatting matching exact financial impact calculations.
"""

import pytest
from backend.engine.allocation.explanations import generate_financial_explanation

def test_explanation_payload_structure():
    """Explanation payload must contain all required structured fields."""
    store = {"id": "STORE_01", "name": "Bangalore Indiranagar", "city": "Bangalore"}
    product = {"id": "PROD_001", "model_name": "Nova Go 5G", "segment": "Budget", "lifecycle_stage": "Peak"}

    exp = generate_financial_explanation(
        store=store,
        product=product,
        recommended_qty=5,
        current_stock=1,
        projected_stock=6,
        forecast_demand=10.0,
        current_woc=0.1,
        projected_woc=0.6,
        net_benefit=15000.0,
        avoided_goodwill_benefit=1500.0,
        margin_contribution=14750.0,
        allocation_cost=1250.0,
    )

    assert "reason_code" in exp
    assert "headline" in exp
    assert "demand_reason" in exp
    assert "financial_benefit" in exp
    assert "financial_cost" in exp
    assert "explanation_text" in exp
    assert "metrics_breakdown" in exp

    assert exp["metrics_breakdown"]["recommended_qty"] == 5
    assert exp["metrics_breakdown"]["net_benefit"] == 15000.0

def test_explanation_matches_financial_impact():
    """Every displayed financial number in text narrative must match calculation exactly."""
    store = {"id": "STORE_01", "name": "MobiMart Indiranagar", "city": "Bangalore"}
    product = {"id": "PROD_040", "model_name": "Zenith Ultra 24", "segment": "Flagship", "lifecycle_stage": "Peak"}

    exp = generate_financial_explanation(
        store=store,
        product=product,
        recommended_qty=3,
        current_stock=1,
        projected_stock=4,
        forecast_demand=4.3,
        current_woc=0.2,
        projected_woc=0.9,
        net_benefit=57250.0,
        avoided_goodwill_benefit=3400.0,
        margin_contribution=54600.0,
        allocation_cost=750.0,
    )

    # Text must explicitly contain exact formatted numbers and product model name
    text = exp["explanation_text"]
    assert "Zenith Ultra 24" in text
    assert "₹54,600.00" in text
    assert "₹3,400.00" in text
    assert "₹750.00" in text
    assert "₹57,250.00" in text

def test_product_id_name_consistency():
    """Ensure recommendation.product_id maps to product_name and matches explanation text."""
    store = {"id": "STORE_02", "name": "MobiMart Phoenix", "city": "Bangalore"}
    product = {"id": "PROD_058", "model_name": "Apex Sovereign 2", "segment": "Flagship", "lifecycle_stage": "Peak"}

    exp = generate_financial_explanation(
        store=store,
        product=product,
        recommended_qty=4,
        current_stock=1,
        projected_stock=5,
        forecast_demand=5.1,
        current_woc=0.2,
        projected_woc=1.0,
        net_benefit=131300.0,
        avoided_goodwill_benefit=6300.0,
        margin_contribution=126000.0,
        allocation_cost=1000.0,
    )

    assert "Apex Sovereign 2" in exp["explanation_text"]
    assert "Apex Sovereign 2" in exp["demand_reason"]
    assert exp["metrics_breakdown"]["product_id"] == "PROD_058"

