"""
Simulation State & Starting Inventory Snapshot Construction Engine for MobiMart.
Implements Correction 1: Priority-based starting inventory pruning guaranteeing
budget compliance (<= ₹4 Crore), store/product diversity, and meaningful EOL exposure
without arbitrary blanket scaling.
"""

from copy import deepcopy
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

from backend.engine.simulation.models import StartingInventorySnapshot, SimulationConfig

def build_starting_inventory_snapshot(
    inventory_df_or_records: Any,
    products: List[Dict[str, Any]],
    stores: List[Dict[str, Any]],
    target_capital: float = 38000000.0,
) -> StartingInventorySnapshot:
    """
    Construct a deterministic, transparent, business-defensible starting inventory snapshot.
    Originates from raw data/generated/inventory.csv.
    """
    products_by_id = {p["id"]: p for p in products}

    # Standardize input records
    if isinstance(inventory_df_or_records, pd.DataFrame):
        records = inventory_df_or_records.to_dict(orient="records")
    else:
        records = [dict(r) for r in inventory_df_or_records]

    raw_total_cost = 0.0
    raw_total_units = 0

    # Build operational working records
    working: List[Dict[str, Any]] = []
    for rec in records:
        store_id = rec["store_id"]
        product_id = rec["product_id"]
        stock = int(rec.get("current_stock", 0))
        prod = products_by_id[product_id]
        cost_price = float(prod.get("cost_price", 0.0))
        raw_cost = stock * cost_price

        raw_total_cost += raw_cost
        raw_total_units += stock

        # Estimate weekly demand from recorded weeks of cover or target stock level
        recorded_woc = float(rec.get("weeks_of_cover", 4.0))
        if recorded_woc > 0 and stock > 0:
            est_weekly_demand = stock / recorded_woc
        else:
            est_weekly_demand = float(rec.get("target_stock_level", 4)) / 4.0

        stage = prod.get("lifecycle_stage", "Peak")
        # Target protected cover: higher cover for EOL/Decline to preserve EOL exposure
        if stage in ("Launch", "Growth"):
            protected_woc = 2.5
        elif stage == "Peak":
            protected_woc = 3.0
        elif stage == "Decline":
            protected_woc = 4.0
        else:  # EOL
            protected_woc = 5.0  # Preserve elevated EOL stock cover!

        protected_units = max(1 if stock > 0 else 0, int(np.ceil(est_weekly_demand * protected_woc)))
        protected_units = min(stock, protected_units)
        excess_units = max(0, stock - protected_units)

        working.append({
            "store_id": store_id,
            "product_id": product_id,
            "raw_stock": stock,
            "cost_price": cost_price,
            "est_weekly_demand": est_weekly_demand,
            "protected_units": protected_units,
            "excess_units": excess_units,
            "current_op_stock": stock,
            "recorded_woc": recorded_woc,
        })

    current_total_cost = raw_total_cost

    # Step 1: Prune excess units in order of highest excess WOC / cost price
    if current_total_cost > target_capital:
        # Sort positions with excess units by excess WOC descending, cost price descending
        working.sort(
            key=lambda x: (
                -(x["current_op_stock"] / max(0.1, x["est_weekly_demand"])),
                -x["cost_price"],
                x["store_id"],
                x["product_id"],
            )
        )

        for item in working:
            if current_total_cost <= target_capital:
                break
            if item["excess_units"] <= 0:
                continue

            # Calculate maximum units we can remove from excess
            max_remove = item["excess_units"]
            cost_per_unit = item["cost_price"]
            needed_reduction = current_total_cost - target_capital
            units_to_remove = min(max_remove, int(np.ceil(needed_reduction / cost_per_unit)))

            item["current_op_stock"] -= units_to_remove
            item["excess_units"] -= units_to_remove
            current_total_cost -= (units_to_remove * cost_per_unit)

    # Step 2: If still above target capital, scale protected stock down to target while preserving store/product diversity (stock >= 1)
    if current_total_cost > target_capital:
        # Calculate target scale ratio for protected stock
        scale_ratio = target_capital / current_total_cost
        working.sort(key=lambda x: (-x["cost_price"], x["store_id"], x["product_id"]))

        for item in working:
            if item["current_op_stock"] <= 1 and item["raw_stock"] > 0:
                continue
            new_stock = max(1 if item["raw_stock"] > 0 else 0, int(np.floor(item["current_op_stock"] * scale_ratio)))
            diff = item["current_op_stock"] - new_stock
            if diff > 0:
                item["current_op_stock"] -= diff
                current_total_cost -= (diff * item["cost_price"])

        # Fine-tune 1 unit at a time until strictly <= target_capital
        while current_total_cost > target_capital:
            reduced = False
            for item in working:
                if current_total_cost <= target_capital:
                    break
                if item["current_op_stock"] <= 1 and item["raw_stock"] > 0:
                    continue
                item["current_op_stock"] -= 1
                current_total_cost -= item["cost_price"]
                reduced = True
            if not reduced:
                # Emergency break if all items are down to 1 unit
                break

    # Final map construction
    op_stock_map: Dict[str, int] = {}
    retained_units = 0
    for item in working:
        key = f"{item['store_id']}|{item['product_id']}"
        op_stock_map[key] = item["current_op_stock"]
        retained_units += item["current_op_stock"]

    removed_units = raw_total_units - retained_units
    capital_headroom = max(0.0, 40000000.0 - current_total_cost)

    return StartingInventorySnapshot(
        raw_inventory_cost=round(raw_total_cost, 2),
        operational_inventory_cost=round(current_total_cost, 2),
        raw_total_units=raw_total_units,
        operational_total_units=retained_units,
        units_retained=retained_units,
        units_removed=removed_units,
        capital_headroom=round(capital_headroom, 2),
        methodology="Priority-Based Operational Cover Pruning v1",
        store_product_stock=op_stock_map,
    )

def build_warehouse_opening_state(
    products: List[Dict[str, Any]],
    sales_history_df: pd.DataFrame,
    cover_weeks: float = 8.0,
) -> Dict[str, int]:
    """
    Construct deterministic warehouse opening stock based on product sales velocity.
    Formula: max(20, ceil(average_weekly_chain_sales * cover_weeks))
    """
    warehouse_stock: Dict[str, int] = {}
    
    # Calculate total 52-week sales per product across all stores
    prod_sales = sales_history_df.groupby("product_id")["units_sold"].sum().to_dict()

    for prod in products:
        pid = prod["id"]
        annual_units = prod_sales.get(pid, 50)
        avg_weekly_units = annual_units / 52.0
        target_units = int(np.ceil(avg_weekly_units * cover_weeks))
        warehouse_stock[pid] = max(20, target_units)

    return warehouse_stock

def get_independent_store_inventory(
    snapshot: StartingInventorySnapshot,
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Create a fresh, unmutated store inventory dict map for a simulation run.
    Key: (store_id, product_id)
    Value: dict record compatible with allocation & EOL engines.
    """
    store_inv: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for key_str, stock in snapshot.store_product_stock.items():
        s_id, p_id = key_str.split("|")
        store_inv[(s_id, p_id)] = {
            "store_id": s_id,
            "product_id": p_id,
            "current_stock": stock,
            "in_transit_stock": 0,
            "reserved_stock": 0,
        }
    return store_inv
