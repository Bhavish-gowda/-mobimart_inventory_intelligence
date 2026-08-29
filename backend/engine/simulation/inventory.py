"""
Inventory Operations & Conservation Engine for MobiMart Simulator.
Handles transfer execution, markdown execution, demand fulfillment, and strict
inventory conservation accounting identity verification.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd

from backend.engine.eol.models import PortfolioTransferResolution, EOLRiskAssessment
from backend.engine.simulation.models import WeeklySimulationResult

def apply_eol_transfers(
    store_inventory: Dict[Tuple[str, str], Dict[str, Any]],
    portfolio_resolution: PortfolioTransferResolution,
    transfer_cost_per_unit: float = 500.0,
) -> Tuple[int, float]:
    """
    Apply portfolio-approved EOL transfers to store inventory records.
    Decreases source store stock, increases destination store stock.
    Returns (total_transferred_units, total_transfer_cost).
    """
    total_transferred_units = 0
    total_transfer_cost = 0.0

    for route in portfolio_resolution.approved_routes:
        qty = route.approved_units
        if qty <= 0:
            continue

        src_key = (route.source_store_id, route.product_id)
        dst_key = (route.destination_store_id, route.product_id)

        # Source inventory lookup
        src_rec = store_inventory.get(src_key)
        if src_rec is not None:
            actual_move = min(qty, src_rec["current_stock"])
            src_rec["current_stock"] -= actual_move
        else:
            actual_move = 0

        if actual_move > 0:
            # Destination inventory lookup
            if dst_key not in store_inventory:
                store_inventory[dst_key] = {
                    "store_id": route.destination_store_id,
                    "product_id": route.product_id,
                    "current_stock": 0,
                    "in_transit_stock": 0,
                }
            store_inventory[dst_key]["current_stock"] += actual_move

            total_transferred_units += actual_move
            total_transfer_cost += (actual_move * transfer_cost_per_unit)

    return total_transferred_units, total_transfer_cost

def apply_eol_markdowns(
    store_inventory: Dict[Tuple[str, str], Dict[str, Any]],
    eol_assessments: List[EOLRiskAssessment],
    products_by_id: Dict[str, Dict[str, Any]],
) -> Tuple[int, float]:
    """
    Apply EOL markdown recommendations.
    Only counts actual markdown loss produced by simulator actions.
    Returns (total_markdowned_units, total_markdown_loss).
    """
    total_markdowned_units = 0
    total_markdown_loss = 0.0

    for assessment in eol_assessments:
        if assessment.recommended_action == "MARKDOWN":
            key = (assessment.store_id, assessment.product_id)
            inv_rec = store_inventory.get(key)
            if inv_rec is None:
                continue

            units = inv_rec["current_stock"]
            if units <= 0:
                continue

            prod = products_by_id.get(assessment.product_id, {})
            cost_price = float(prod.get("cost_price", 0.0))
            markdown_pct = float(assessment.markdown_option.assumptions.get("markdown_pct", 0.30))

            loss = units * cost_price * markdown_pct
            total_markdowned_units += units
            total_markdown_loss += loss

    return total_markdowned_units, round(total_markdown_loss, 2)

def fulfill_weekly_demand(
    store_inventory: Dict[Tuple[str, str], Dict[str, Any]],
    week_sales_df: pd.DataFrame,
    products_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Fulfill week W customer demand against available store inventory.
    Reveals demand_units for week W and updates ending inventory.
    """
    total_demand_units = 0
    total_fulfilled_units = 0
    total_lost_sales_units = 0
    total_lost_sales_value = 0.0
    total_revenue = 0.0
    total_gross_margin = 0.0
    total_cogs = 0.0
    stockout_obs = 0
    positive_demand_obs = 0

    for _, row in week_sales_df.iterrows():
        s_id = row["store_id"]
        p_id = row["product_id"]
        demand = int(row["demand_units"])

        key = (s_id, p_id)
        inv_rec = store_inventory.get(key)
        available = inv_rec["current_stock"] if inv_rec else 0

        if demand > 0:
            positive_demand_obs += 1

        fulfilled = min(demand, available)
        lost = max(0, demand - fulfilled)

        if lost > 0:
            stockout_obs += 1

        prod = products_by_id[p_id]
        retail_price = float(prod.get("retail_price", 0.0))
        cost_price = float(prod.get("cost_price", 0.0))

        rev = fulfilled * retail_price
        cogs = fulfilled * cost_price
        margin = rev - cogs
        lost_val = lost * retail_price

        total_demand_units += demand
        total_fulfilled_units += fulfilled
        total_lost_sales_units += lost
        total_lost_sales_value += lost_val
        total_revenue += rev
        total_gross_margin += margin
        total_cogs += cogs

        # Update inventory stock
        if inv_rec:
            inv_rec["current_stock"] -= fulfilled

    return {
        "demand_units": total_demand_units,
        "fulfilled_units": total_fulfilled_units,
        "lost_sales_units": total_lost_sales_units,
        "lost_sales_value": round(total_lost_sales_value, 2),
        "stockout_observations": stockout_obs,
        "positive_demand_observations": positive_demand_obs,
        "revenue": round(total_revenue, 2),
        "gross_margin": round(total_gross_margin, 2),
        "cogs": round(total_cogs, 2),
    }

def verify_inventory_conservation(
    starting_store_units: int,
    allocated_units: int,
    fulfilled_units: int,
    ending_store_units: int,
) -> bool:
    """
    Verify fundamental inventory conservation identity:
    starting_units + allocated_additions - fulfilled_sales == ending_units.
    Note: Transfers move units between stores (net zero sum). Markdowns sell or write down stock.
    """
    expected_ending = starting_store_units + allocated_units - fulfilled_units
    if expected_ending != ending_store_units:
        raise ValueError(
            f"Inventory conservation failure! Starting ({starting_store_units}) + "
            f"Allocated ({allocated_units}) - Fulfilled ({fulfilled_units}) = "
            f"Expected {expected_ending}, but got Actual Ending ({ending_store_units})."
        )
    return True
