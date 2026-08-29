"""
Financial Explanation Engine for MobiMart Allocation Recommendations.
Generates 100% deterministic, calculated, structured explanations directly from
forecasted demand, inventory metrics, and financial impact models.

ZERO LLM DEPENDENCY. All numbers and reasons are computed directly from business logic.
"""

from typing import Dict, Any

def generate_financial_explanation(
    store: Dict[str, Any],
    product: Dict[str, Any],
    recommended_qty: int,
    current_stock: int,
    projected_stock: int,
    forecast_demand: float,
    current_woc: float,
    projected_woc: float,
    net_benefit: float,
    avoided_goodwill_benefit: float,
    margin_contribution: float,
    allocation_cost: float,
) -> Dict[str, Any]:
    """
    Generate structured, verified financial explanation payload for a store recommendation.
    """
    store_name = store.get("name", store["id"])
    model_name = product.get("model_name", product["id"])
    segment = product["segment"]
    stage = product.get("lifecycle_stage", "Peak")

    # Determine reason code & headline
    if current_woc < 1.0 and forecast_demand >= 5.0:
        reason_code = "CRITICAL_STOCKOUT_PREVENTION"
        headline = f"CRITICAL STOCKOUT RISK IN {store['city'].upper()}"
    elif current_woc < 2.0:
        reason_code = "HIGH_STOCKOUT_RISK"
        headline = "STOCKOUT PREVENTION + HIGH DEMAND"
    elif stage == "Launch":
        reason_code = "NEW_PRODUCT_LAUNCH_SURGE"
        headline = "NEW PRODUCT LAUNCH STOCKING"
    elif segment == "Flagship":
        reason_code = "HIGH_MARGIN_FLAGSHIP_OPPORTUNITY"
        headline = "FLAGSHIP CAPITAL MARGIN OPTIMIZATION"
    else:
        reason_code = "BALANCED_REPLENISHMENT"
        headline = "OPTIMAL INVENTORY REPLENISHMENT"

    # Narrative sentences constructed from exact calculated figures
    demand_reason = (
        f"Forecasted weekly demand for {model_name} at {store_name} is {forecast_demand:.1f} units/week, "
        f"while current store stock is only {current_stock} units ({current_woc:.1f} weeks of cover)."
    )

    financial_benefit = (
        f"Allocating +{recommended_qty} units increases stock cover to {projected_woc:.1f} weeks, "
        f"generating ₹{margin_contribution:,.2f} in expected gross margin contribution and "
        f"₹{avoided_goodwill_benefit:,.2f} in avoided customer dissatisfaction goodwill benefit."
    )

    financial_cost = f"Incurs ₹{allocation_cost:,.2f} in warehouse handling logistics fees."

    net_summary = (
        f"Delivers a total net financial benefit of ₹{net_benefit:,.2f} under a warehouse unit allocation cost of "
        f"₹{allocation_cost/max(1, recommended_qty):,.2f}/unit."
    )

    explanation_text = f"{headline}: {demand_reason} {financial_benefit} {financial_cost} {net_summary}"

    return {
        "reason_code": reason_code,
        "headline": headline,
        "demand_reason": demand_reason,
        "financial_benefit": financial_benefit,
        "financial_cost": financial_cost,
        "net_summary": net_summary,
        "explanation_text": explanation_text,
        "metrics_breakdown": {
            "store_id": store["id"],
            "product_id": product["id"],
            "recommended_qty": recommended_qty,
            "current_stock": current_stock,
            "projected_stock": projected_stock,
            "forecast_weekly_demand": round(forecast_demand, 2),
            "current_woc": round(current_woc, 2),
            "projected_woc": round(projected_woc, 2),
            "net_benefit": round(net_benefit, 2),
            "avoided_goodwill_benefit": round(avoided_goodwill_benefit, 2),
            "avoided_stockout_loss": round(avoided_goodwill_benefit, 2),  # Backward compatibility alias
            "margin_contribution": round(margin_contribution, 2),
            "allocation_cost": round(allocation_cost, 2),
        },
    }
