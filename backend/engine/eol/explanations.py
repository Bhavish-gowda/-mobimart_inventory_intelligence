"""
Deterministic Financial Explanation Engine for MobiMart EOL Engine.
Generates non-LLM, rupee-accurate explanations comparing Markdown, Transfer, and Hold options.
"""

from typing import Dict, Any, List
from backend.engine.eol.models import EOLActionOption

def generate_eol_explanation(
    risk_level: str,
    risk_score: float,
    store_id: str,
    product_name: str,
    product_id: str,
    inventory_units: int,
    weeks_of_cover: float,
    successor_id: str,
    weeks_to_successor: float,
    risk_factors: List[str],
    markdown_opt: EOLActionOption,
    transfer_opt: EOLActionOption,
    hold_opt: EOLActionOption,
    recommended_action: str,
) -> str:
    """
    Generate an explainable rupee-proof sentence for EOL decision.

    Template example from specification Section 12:
    "CRITICAL EOL RISK: PROD_054 has 9.8 weeks of inventory cover while its successor launches in 2 weeks.
    Holding the stock is expected to expose ₹X to markdown risk. Transferring 20 units to STORE_07 is expected
    to reduce exposure by ₹Y after ₹10,000 transfer cost. Transfer is therefore recommended."
    """
    succ_clause = (
        f" while its successor ({successor_id}) launches in {weeks_to_successor:.1f} weeks"
        if successor_id and weeks_to_successor is not None
        else ""
    )

    header = f"{risk_level} EOL RISK ({product_id} / {product_name}): {inventory_units} units in stock ({weeks_of_cover:.1f} weeks of cover){succ_clause}."

    hold_loss = hold_opt.net_financial_loss
    markdown_loss = markdown_opt.net_financial_loss
    transfer_loss = transfer_opt.net_financial_loss

    if recommended_action == "TRANSFER":
        transferred_units = transfer_opt.units_affected
        target_store = transfer_opt.target_store_id
        cost = transfer_opt.expected_cost
        savings_vs_hold = max(0.0, hold_loss - transfer_loss)
        body = (
            f" Holding the stock is expected to expose ₹{hold_loss:,.2f} to markdown/holding loss. "
            f"Transferring {transferred_units} units to {target_store} is expected to reduce exposure by "
            f"₹{savings_vs_hold:,.2f} after ₹{cost:,.2f} transfer cost. TRANSFER is therefore recommended."
        )
    elif recommended_action == "MARKDOWN":
        savings_vs_hold = max(0.0, hold_loss - markdown_loss)
        body = (
            f" Holding the stock is expected to expose ₹{hold_loss:,.2f} to terminal loss. "
            f"Applying an immediate MARKDOWN is expected to limit financial loss to ₹{markdown_loss:,.2f}, "
            f"saving ₹{savings_vs_hold:,.2f} compared to holding. MARKDOWN is therefore recommended."
        )
    else:  # HOLD
        body = (
            f" Holding stock exposes ₹{hold_loss:,.2f} expected loss over the remaining period, which is lower "
            f"than markdown loss (₹{markdown_loss:,.2f}) or transfer costs. HOLD is therefore recommended."
        )

    return header + body
