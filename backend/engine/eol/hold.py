"""
Hold Economics Engine for MobiMart EOL Engine.
Calculates the expected financial loss and holding exposure of keeping
inventory at the current store through the remaining lifecycle or successor window.
"""

from typing import Dict, Any
from backend.engine.eol.models import EOLActionOption

def evaluate_hold_option(
    product: Dict[str, Any],
    inventory_units: int,
    forecast_weekly_demand: float,
    current_week: int = 24,
) -> EOLActionOption:
    """
    Calculate deterministic expected financial impact of holding inventory.

    Formulas:
        remaining_weeks = max(1.0, expected_successor_week - current_week) [or 4.0 default]
        expected_hold_sales = min(inventory_units, forecast_weekly_demand * remaining_weeks)
        unsold_units = max(0, inventory_units - expected_hold_sales)
        carrying_cost = inventory_units * cost_price * (0.005 * remaining_weeks)
        terminal_markdown_loss = unsold_units * cost_price * terminal_markdown_pct
        net_financial_loss = terminal_markdown_loss + carrying_cost
    """
    if inventory_units <= 0:
        return EOLActionOption(
            action="HOLD",
            expected_cost=0.0,
            expected_recovery=0.0,
            net_financial_loss=0.0,
            units_affected=0,
            target_store_id=None,
            assumptions={"remaining_weeks": 0.0, "cost_basis": 0.0},
            explanation="HOLD option: 0 units in stock, zero holding exposure.",
        )

    cost_price = float(product.get("cost_price", 0.0))
    retail_price = float(product.get("retail_price", 0.0))
    stage = product.get("lifecycle_stage", "Peak")

    expected_successor_week = product.get("expected_successor_week")
    if expected_successor_week is not None and expected_successor_week > current_week:
        remaining_weeks = max(1.0, float(expected_successor_week - current_week))
    elif stage == "EOL":
        remaining_weeks = 2.0
    elif stage == "Decline":
        remaining_weeks = 4.0
    else:
        remaining_weeks = 4.0

    expected_hold_sales = min(float(inventory_units), forecast_weekly_demand * remaining_weeks)
    unsold_units = max(0.0, float(inventory_units) - expected_hold_sales)

    # Terminal markdown discount when holding period ends and successor arrives
    base_markdown_pct = float(product.get("markdown_percentage", 0.28))
    terminal_markdown_pct = min(0.50, max(0.35, base_markdown_pct * 1.5))

    cost_basis = inventory_units * cost_price
    carrying_cost = cost_basis * (0.005 * remaining_weeks)  # 0.5% per week holding cost
    terminal_markdown_loss = unsold_units * cost_price * terminal_markdown_pct

    expected_hold_revenue = expected_hold_sales * retail_price
    terminal_salvage_recovery = unsold_units * retail_price * (1.0 - terminal_markdown_pct)
    expected_recovery = round(expected_hold_revenue + terminal_salvage_recovery, 2)

    net_financial_loss = round(terminal_markdown_loss + carrying_cost, 2)

    explanation = (
        f"HOLD option: Retain stock over {remaining_weeks:.1f} weeks. Forecast demand yields "
        f"{expected_hold_sales:.1f} unit sales, leaving {unsold_units:.1f} unsold units. "
        f"Exposes ₹{carrying_cost:,.2f} carrying cost and ₹{terminal_markdown_loss:,.2f} terminal markdown loss. "
        f"Total expected hold loss: ₹{net_financial_loss:,.2f}."
    )

    return EOLActionOption(
        action="HOLD",
        expected_cost=round(carrying_cost, 2),
        expected_recovery=expected_recovery,
        net_financial_loss=net_financial_loss,
        units_affected=inventory_units,
        target_store_id=None,
        assumptions={
            "remaining_weeks": remaining_weeks,
            "expected_hold_sales": expected_hold_sales,
            "unsold_units": unsold_units,
            "terminal_markdown_pct": terminal_markdown_pct,
            "carrying_cost": carrying_cost,
            "terminal_markdown_loss": terminal_markdown_loss,
        },
        explanation=explanation,
    )
