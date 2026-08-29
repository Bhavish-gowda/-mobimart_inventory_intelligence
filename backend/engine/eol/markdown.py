"""
Markdown Economics Engine for MobiMart EOL Engine.
Evaluates the financial impact, expected loss, and expected recovery of
marking down excess/EOL inventory at the current store position.
"""

from typing import Dict, Any
from backend.engine.eol.models import EOLActionOption

def evaluate_markdown_option(
    product: Dict[str, Any],
    inventory_units: int,
    custom_markdown_pct: float = None,
) -> EOLActionOption:
    """
    Calculate financial economics of applying an immediate markdown discount to inventory.

    Formulas:
        cost_basis = inventory_units * cost_price
        markdown_pct = custom_markdown_pct or product['markdown_percentage']
        markdown_loss = cost_basis * markdown_pct
        discounted_retail = retail_price * (1.0 - markdown_pct)
        expected_recovery = inventory_units * discounted_retail
        net_financial_loss = markdown_loss
    """
    if inventory_units <= 0:
        return EOLActionOption(
            action="MARKDOWN",
            expected_cost=0.0,
            expected_recovery=0.0,
            net_financial_loss=0.0,
            units_affected=0,
            target_store_id=None,
            assumptions={"markdown_pct": 0.0, "cost_basis": 0.0},
            explanation="MARKDOWN option: 0 units in stock, zero markdown loss.",
        )

    cost_price = float(product.get("cost_price", 0.0))
    retail_price = float(product.get("retail_price", 0.0))

    if custom_markdown_pct is not None:
        markdown_pct = float(custom_markdown_pct)
    else:
        markdown_pct = float(product.get("markdown_percentage", 0.28))

    cost_basis = inventory_units * cost_price
    retail_basis = inventory_units * retail_price

    discounted_retail = retail_price * (1.0 - markdown_pct)
    expected_recovery = round(inventory_units * discounted_retail, 2)
    markdown_discount_amount = round(retail_basis * markdown_pct, 2)
    markdown_cost_loss = round(cost_basis * markdown_pct, 2)

    net_financial_loss = markdown_cost_loss

    explanation = (
        f"MARKDOWN option: Apply {int(markdown_pct * 100)}% discount to {inventory_units} units. "
        f"Inventory cost basis: ₹{cost_basis:,.2f}. Customer discount: ₹{markdown_discount_amount:,.2f}. "
        f"Expected recovery: ₹{expected_recovery:,.2f}. Expected markdown loss: ₹{net_financial_loss:,.2f}."
    )

    return EOLActionOption(
        action="MARKDOWN",
        expected_cost=0.0,  # No out-of-pocket transfer cost
        expected_recovery=expected_recovery,
        net_financial_loss=net_financial_loss,
        units_affected=inventory_units,
        target_store_id=None,
        assumptions={
            "markdown_pct": markdown_pct,
            "cost_price": cost_price,
            "retail_price": retail_price,
            "cost_basis": cost_basis,
            "retail_basis": retail_basis,
            "markdown_discount_amount": markdown_discount_amount,
            "markdown_cost_loss": markdown_cost_loss,
        },
        explanation=explanation,
    )
