"""
Naive Baseline Allocation Engine for MobiMart.
Implements Last-4-Week Proportional Allocation:
Allocates available warehouse inventory proportional to observed store sales
over the 4 completed weeks prior to the planning week.
Uses 100% deterministic integer rounding and remainder resolution.
Zero future leakage, zero forecasting models, zero financial marginal calculations.
"""

from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

def allocate_baseline_inventory(
    sales_history_df: pd.DataFrame,
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    inventory_records: List[Dict[str, Any]],
    planning_week: int,
    warehouse_stock: Dict[str, int],
    high_risk_eol_product_ids: set,
    capital_budget_limit: float = 40000000.0,
    lookback_weeks: int = 4,
) -> Dict[Tuple[str, str], int]:
    """
    Execute Last-4-Week Proportional Allocation for planning_week.
    Returns dict mapping (store_id, product_id) -> allocated_units.
    """
    products_by_id = {p["id"]: p for p in products}
    stores_by_id = {s["id"]: s for s in stores}

    # Calculate initial capital deployed across stores
    initial_capital_deployed = 0.0
    for inv in inventory_records:
        cost = products_by_id[inv["product_id"]]["cost_price"]
        stock = inv.get("current_stock", 0) + inv.get("in_transit_stock", 0)
        initial_capital_deployed += stock * cost

    if capital_budget_limit >= initial_capital_deployed:
        effective_new_capital_budget = capital_budget_limit - initial_capital_deployed
    else:
        effective_new_capital_budget = capital_budget_limit

    new_capital_allocated = 0.0

    # Determine lookback range [start_wk, end_wk]
    end_wk = planning_week - 1
    start_wk = max(1, planning_week - lookback_weeks)

    if end_wk < 1:
        # Week 1: No completed historical weeks exist
        return {}

    # Filter sales history for lookback period
    hist_df = sales_history_df[
        (sales_history_df["week_number"] >= start_wk) &
        (sales_history_df["week_number"] <= end_wk)
    ]

    # Calculate sales by (product_id, store_id)
    sales_by_pair = hist_df.groupby(["product_id", "store_id"])["units_sold"].sum().to_dict()
    sales_by_prod = hist_df.groupby("product_id")["units_sold"].sum().to_dict()

    allocated_units: Dict[Tuple[str, str], int] = {}

    # Iterate through products deterministically sorted by product_id
    for prod in sorted(products, key=lambda p: p["id"]):
        p_id = prod["id"]
        avail_wh = warehouse_stock.get(p_id, 0)
        if avail_wh <= 0:
            continue

        # EOL Rule: Block warehouse allocation for high-risk EOL SKUs
        if p_id in high_risk_eol_product_ids:
            continue

        tot_prod_sales = sales_by_prod.get(p_id, 0)
        if tot_prod_sales <= 0:
            continue  # Zero historical sales -> no allocation

        cost_price = float(prod["cost_price"])

        # Determine target allocation volume for product across stores
        # Allocation target = min(avail_wh, int(ceil(tot_prod_sales * 0.25)))
        target_product_alloc = min(avail_wh, max(1, int(np.ceil(tot_prod_sales * 0.25))))

        # Calculate raw proportional share per store
        shares: List[Dict[str, Any]] = []
        floored_sum = 0

        for store in stores:
            s_id = store["id"]
            st_sales = sales_by_pair.get((p_id, s_id), 0)
            if st_sales <= 0:
                continue

            exact_share = target_product_alloc * (st_sales / float(tot_prod_sales))
            floored = int(np.floor(exact_share))
            remainder = exact_share - floored

            floored_sum += floored
            shares.append({
                "store_id": s_id,
                "floored": floored,
                "remainder": remainder,
                "st_sales": st_sales,
            })

        # Distribute remaining fractional units deterministically
        remain_units = target_product_alloc - floored_sum
        shares.sort(key=lambda s: (-s["remainder"], -s["st_sales"], s["store_id"]))

        for i in range(min(remain_units, len(shares))):
            shares[i]["floored"] += 1

        # Commit unit allocations respecting warehouse stock and capital budget
        for item in shares:
            s_id = item["store_id"]
            qty = item["floored"]
            if qty <= 0:
                continue

            # Check warehouse availability
            actual_qty = min(qty, warehouse_stock.get(p_id, 0))
            if actual_qty <= 0:
                continue

            # Check capital budget constraint
            cost = actual_qty * cost_price
            if new_capital_allocated + cost > effective_new_capital_budget:
                # Reduce units to fit remaining budget
                avail_cap = effective_new_capital_budget - new_capital_allocated
                if avail_cap <= 0:
                    break
                actual_qty = int(np.floor(avail_cap / cost_price))
                if actual_qty <= 0:
                    break
                cost = actual_qty * cost_price

            # Commit allocation
            key = (s_id, p_id)
            allocated_units[key] = actual_qty
            warehouse_stock[p_id] -= actual_qty
            new_capital_allocated += cost

    return allocated_units
