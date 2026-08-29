"""
Store-to-Store Transfer Search & Economics Engine for MobiMart EOL Engine.
Evaluates store transfer opportunities to relocate excess/EOL stock to target stores
with active customer demand and low weeks of cover.

Uses STORE_TRANSFER_COST_PER_UNIT = ₹500 (implementation assumption).
Strictly enforces that target stores have both observed historical demand and
active forecast demand.
"""

from typing import Dict, List, Any, Optional, Tuple
from backend.engine.eol.models import EOLActionOption
from backend.engine.eol.config import STORE_TRANSFER_COST_PER_UNIT, TARGET_WEEKS_OF_COVER


def _has_meaningful_historical_demand(
    sales_history_df: Any,
    store_id: str,
    product_id: str,
    current_week: int,
) -> bool:
    """Return whether a destination has observed demand before the decision week.

    The allocation forecast deliberately provides a cold-start baseline for a
    new SKU.  That is useful for replenishment, but it must not make an EOL
    transfer valid: this engine requires evidence of demand at the destination
    and must not use post-decision sales.
    """
    history = sales_history_df[
        (sales_history_df["store_id"] == store_id)
        & (sales_history_df["product_id"] == product_id)
        & (sales_history_df["week_number"] < current_week)
    ]
    return not history.empty and float(history["units_sold"].sum()) > 0.0

def search_best_transfer_destination(
    source_store_id: str,
    product: Dict[str, Any],
    inventory_units: int,
    source_woc: float,
    all_stores: List[Dict[str, Any]],
    all_inventory: List[Dict[str, Any]],
    sales_history_df: Any,
    forecast_func: Any,
    current_week: int = 24,
    historical_demand_positions: Optional[set] = None,
) -> Optional[Dict[str, Any]]:
    """
    Search candidate target stores for transfer destination.

    Filters:
      - Must not be source store
      - Must have observed historical demand before the decision week
      - Must have forecast_weekly_demand > 0.0
      - Must have current_woc < TARGET_WEEKS_OF_COVER (4.0)
      - Source must retain its own TARGET_WEEKS_OF_COVER

    Returns:
      Best candidate dict: {
          "store_id": str,
          "forecast_weekly_demand": float,
          "current_stock": int,
          "current_woc": float,
          "demand_shortfall_units": int,
          "units_to_transfer": int,
      } or None if no valid candidate exists.
    """
    product_id = product["id"]

    # Only inventory above the source's target cover is transferable.  This
    # avoids turning a source shortage into a destination replenishment.
    if source_woc <= TARGET_WEEKS_OF_COVER:
        return None
    source_forecast = inventory_units / source_woc
    source_excess_units = max(
        0,
        int(inventory_units - (TARGET_WEEKS_OF_COVER * source_forecast)),
    )
    if source_excess_units <= 0:
        return None

    # Map inventory records by store_id
    inv_by_store = {
        rec["store_id"]: rec
        for rec in all_inventory
        if rec["product_id"] == product_id
    }

    candidates: List[Dict[str, Any]] = []

    for store in all_stores:
        st_id = store["id"]
        if st_id == source_store_id:
            continue

        has_demand = (
            (st_id, product_id) in historical_demand_positions
            if historical_demand_positions is not None
            else _has_meaningful_historical_demand(
                sales_history_df, st_id, product_id, current_week
            )
        )
        if not has_demand:
            continue

        inv_rec = inv_by_store.get(st_id, {"current_stock": 0, "in_transit_stock": 0})
        st_stock = int(inv_rec.get("current_stock", 0))

        # Calculate forecast demand for target store
        forecast_res = forecast_func(sales_history_df, store, product, current_week)
        st_demand = forecast_res.forecast_weekly_demand

        if st_demand <= 0.0:
            continue  # A transfer to a store with NO demand is NOT a valid recommendation

        st_woc = st_stock / st_demand if st_demand > 0 else 99.0

        if st_woc >= TARGET_WEEKS_OF_COVER:
            continue  # Already well stocked

        # Target demand shortfall = stock needed to reach target WOC
        shortfall = max(0, int(round((TARGET_WEEKS_OF_COVER * st_demand) - st_stock)))
        if shortfall <= 0:
            continue

        transferable_units = min(source_excess_units, shortfall)
        if transferable_units <= 0:
            continue

        candidates.append({
            "store_id": st_id,
            "forecast_weekly_demand": round(st_demand, 2),
            "current_stock": st_stock,
            "current_woc": round(st_woc, 2),
            "demand_shortfall_units": shortfall,
            "units_to_transfer": transferable_units,
            "source_excess_units": source_excess_units,
        })

    if not candidates:
        return None

    # Rank by max transferable units, then highest forecast demand
    candidates.sort(key=lambda c: (c["units_to_transfer"], c["forecast_weekly_demand"]), reverse=True)
    return candidates[0]

def evaluate_transfer_option(
    source_store_id: str,
    product: Dict[str, Any],
    inventory_units: int,
    source_woc: float,
    all_stores: List[Dict[str, Any]],
    all_inventory: List[Dict[str, Any]],
    sales_history_df: Any,
    forecast_func: Any,
    current_week: int = 24,
    historical_demand_positions: Optional[set] = None,
) -> EOLActionOption:
    """
    Calculate financial economics of store-to-store inventory transfer.

    Formula:
        transfer_units = min(source_excess_units, target_demand_shortfall)
        logistics_cost = transfer_units * STORE_TRANSFER_COST_PER_UNIT (₹500)
        remaining_units = inventory_units - transfer_units
        remaining_source_markdown_loss = remaining_units * cost_price * markdown_pct
        net_financial_loss = logistics_cost + remaining_source_markdown_loss
    """
    if inventory_units <= 0:
        return EOLActionOption(
            action="TRANSFER",
            expected_cost=0.0,
            expected_recovery=0.0,
            net_financial_loss=0.0,
            units_affected=0,
            target_store_id=None,
            assumptions={"transfer_cost_per_unit": STORE_TRANSFER_COST_PER_UNIT},
            explanation="TRANSFER option: 0 units in stock, transfer not applicable.",
        )

    best_candidate = search_best_transfer_destination(
        source_store_id=source_store_id,
        product=product,
        inventory_units=inventory_units,
        source_woc=source_woc,
        all_stores=all_stores,
        all_inventory=all_inventory,
        sales_history_df=sales_history_df,
        forecast_func=forecast_func,
        current_week=current_week,
        historical_demand_positions=historical_demand_positions,
    )

    cost_price = float(product.get("cost_price", 0.0))
    retail_price = float(product.get("retail_price", 0.0))
    markdown_pct = float(product.get("markdown_percentage", 0.28))

    if not best_candidate:
        # Invalid / impossible transfer option
        return EOLActionOption(
            action="TRANSFER",
            expected_cost=0.0,
            expected_recovery=0.0,
            net_financial_loss=float("inf"),
            units_affected=0,
            target_store_id=None,
            assumptions={
                "transfer_cost_per_unit": STORE_TRANSFER_COST_PER_UNIT,
                "reason": "No candidate store with demand shortfall found",
            },
            explanation="TRANSFER option: Rejected (no target store with active demand and inventory shortfall).",
        )

    target_store_id = best_candidate["store_id"]
    units_to_transfer = best_candidate["units_to_transfer"]
    logistics_cost = round(units_to_transfer * STORE_TRANSFER_COST_PER_UNIT, 2)

    remaining_units = inventory_units - units_to_transfer
    remaining_source_markdown_loss = round(remaining_units * cost_price * markdown_pct, 2)

    expected_recovery = round(units_to_transfer * retail_price + remaining_units * retail_price * (1 - markdown_pct), 2)
    net_financial_loss = round(logistics_cost + remaining_source_markdown_loss, 2)

    explanation = (
        f"TRANSFER option: Relocate {units_to_transfer} units from {source_store_id} to {target_store_id} "
        f"at ₹{STORE_TRANSFER_COST_PER_UNIT:.0f}/unit (Logistics cost: ₹{logistics_cost:,.2f}). "
        f"Avoids markdown loss on transferred stock. Net expected transfer option loss: ₹{net_financial_loss:,.2f}."
    )

    return EOLActionOption(
        action="TRANSFER",
        expected_cost=logistics_cost,
        expected_recovery=expected_recovery,
        net_financial_loss=net_financial_loss,
        units_affected=units_to_transfer,
        target_store_id=target_store_id,
        assumptions={
            "transfer_cost_per_unit": STORE_TRANSFER_COST_PER_UNIT,
            "target_store_id": target_store_id,
            "units_transferred": units_to_transfer,
            "logistics_cost": logistics_cost,
            "target_weekly_demand": best_candidate["forecast_weekly_demand"],
            "target_current_woc": best_candidate["current_woc"],
            "destination_shortfall_units": best_candidate["demand_shortfall_units"],
            "source_excess_units": best_candidate["source_excess_units"],
            "remaining_units": remaining_units,
            "remaining_source_markdown_loss": remaining_source_markdown_loss,
        },
        explanation=explanation,
    )
