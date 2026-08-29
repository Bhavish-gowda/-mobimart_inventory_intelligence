"""
Deterministic EOL Risk Scoring Engine for MobiMart.
Calculates a 0.0 to 100.0 EOL risk score based on product lifecycle stage,
successor launch proximity/confidence, inventory excess (weeks of cover),
and demand decline velocity.
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from backend.engine.eol.config import (
    RISK_WEIGHTS,
    RISK_THRESHOLDS,
    TARGET_WEEKS_OF_COVER,
)

def calculate_weeks_of_cover(inventory_units: int, forecast_weekly_demand: float) -> float:
    """Safely calculate weeks of cover for inventory position."""
    if forecast_weekly_demand <= 0.0:
        return 99.0 if inventory_units > 0 else 0.0
    return float(inventory_units / forecast_weekly_demand)

def calculate_eol_risk_score(
    product: Dict[str, Any],
    inventory_units: int,
    forecast_weekly_demand: float,
    recent_sales_velocity: float,
    rolling_avg: float,
    current_week: int = 24,
) -> Tuple[float, str, List[str], str]:
    """
    Calculate deterministic EOL risk score, risk level, risk factors, and summary explanation.

    Returns:
        (risk_score, risk_level, risk_factors, summary_explanation)
    """
    # 0. Zero inventory check: No stock at risk means zero risk!
    if inventory_units <= 0:
        return (
            0.0,
            "LOW",
            ["Zero inventory in stock"],
            f"LOW EOL RISK: {product.get('model_name', product['id'])} has 0 units in stock.",
        )

    risk_factors: List[str] = []

    # 1. Lifecycle Stage Risk (Weight: 30%)
    lifecycle_stage = product.get("lifecycle_stage", "Peak")
    if lifecycle_stage == "EOL":
        lifecycle_score = 100.0
        risk_factors.append("Product is in End-Of-Life (EOL) stage")
    elif lifecycle_stage == "Decline":
        lifecycle_score = 65.0
        risk_factors.append("Product is in Decline stage")
    elif lifecycle_stage == "Peak":
        lifecycle_score = 15.0
    elif lifecycle_stage in ("Growth", "Launch"):
        lifecycle_score = 0.0
    else:
        lifecycle_score = 10.0

    # 2. Successor Launch Proximity & Confidence Risk (Weight: 25%)
    successor_id = product.get("successor_product_id")
    expected_successor_week = product.get("expected_successor_week")
    is_rumoured = bool(product.get("is_rumoured", False))
    raw_confidence = float(product.get("launch_confidence", 1.0))
    confidence = raw_confidence if not is_rumoured else min(raw_confidence, 0.70)

    successor_score = 0.0
    weeks_to_successor: Optional[float] = None

    if successor_id and expected_successor_week is not None:
        weeks_to_successor = float(expected_successor_week - current_week)
        if weeks_to_successor <= 0:
            raw_successor_score = 100.0
            succ_desc = "imminent or already launched"
        elif weeks_to_successor <= 12:
            raw_successor_score = max(0.0, 100.0 * (1.0 - weeks_to_successor / 12.0))
            succ_desc = f"launching in {weeks_to_successor:.1f} weeks"
        else:
            raw_successor_score = 0.0
            succ_desc = f"launching in {weeks_to_successor:.1f} weeks"

        # Confirmed vs Rumoured weighting
        successor_score = raw_successor_score * confidence
        status_str = "Rumoured" if is_rumoured else "Confirmed"
        if successor_score > 10.0:
            risk_factors.append(
                f"{status_str} successor ({successor_id}) {succ_desc} (confidence: {int(confidence * 100)}%)"
            )

    # 3. Inventory Excess / Weeks of Cover Risk (Weight: 25%)
    woc = calculate_weeks_of_cover(inventory_units, forecast_weekly_demand)
    if forecast_weekly_demand <= 0.0:
        excess_woc_score = 100.0
        risk_factors.append(f"Zero forecast demand with {inventory_units} units in stock")
    elif woc > TARGET_WEEKS_OF_COVER:
        excess_weeks = woc - TARGET_WEEKS_OF_COVER
        excess_woc_score = min(100.0, (excess_weeks / 8.0) * 100.0)
        risk_factors.append(
            f"High inventory cover: {woc:.1f} weeks of cover (target: {TARGET_WEEKS_OF_COVER:.1f} weeks)"
        )
    else:
        excess_woc_score = 0.0

    # 4. Demand Decline Risk (Weight: 20%)
    if rolling_avg > 0.0:
        velocity_ratio = recent_sales_velocity / rolling_avg
        if velocity_ratio < 1.0:
            decline_score = min(100.0, (1.0 - velocity_ratio) * 100.0)
            if decline_score > 15.0:
                risk_factors.append(
                    f"Declining sales velocity ({recent_sales_velocity:.1f} units/wk vs {rolling_avg:.1f} rolling avg)"
                )
        else:
            decline_score = 0.0
    else:
        decline_score = 50.0 if forecast_weekly_demand <= 0.0 else 0.0

    # Combine weighted score components
    w_life = RISK_WEIGHTS.get("lifecycle", 0.30)
    w_succ = RISK_WEIGHTS.get("successor", 0.25)
    w_woc = RISK_WEIGHTS.get("excess_woc", 0.25)
    w_decl = RISK_WEIGHTS.get("demand_decline", 0.20)

    raw_total_score = (
        (lifecycle_score * w_life)
        + (successor_score * w_succ)
        + (excess_woc_score * w_woc)
        + (decline_score * w_decl)
    )

    final_score = float(np.clip(round(raw_total_score, 1), 0.0, 100.0))

    # Determine risk level from thresholds
    if final_score >= RISK_THRESHOLDS["CRITICAL"]:
        risk_level = "CRITICAL"
    elif final_score >= RISK_THRESHOLDS["HIGH"]:
        risk_level = "HIGH"
    elif final_score >= RISK_THRESHOLDS["MEDIUM"]:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    prod_name = product.get("model_name", product["id"])
    factor_text = "; ".join(risk_factors) if risk_factors else "Normal inventory position"
    summary_explanation = (
        f"{risk_level} EOL RISK ({final_score:.1f}/100): {prod_name} has {inventory_units} units "
        f"({woc:.1f} WOC). Primary factors: {factor_text}."
    )

    return final_score, risk_level, risk_factors, summary_explanation
