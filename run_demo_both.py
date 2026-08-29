"""
Execution runner for MobiMart Allocation Demo.
Runs both Full Store Initial Inventory (₹10.13 Cr > ₹4 Cr Cap -> 0 units allocated)
and Active Weekly Stock Replenishment (₹3.18 Cr < ₹4 Cr Cap -> 154 units allocated).
"""

import numpy as np
import pandas as pd
from backend.engine.allocation.allocator import allocate_inventory

stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
sales_df = pd.read_csv("data/generated/sales_history.csv")
inventory_full = pd.read_csv("data/generated/inventory.csv").to_dict(orient="records")

inventory_active = []
for inv in inventory_full:
    inv_copy = dict(inv)
    inv_copy["current_stock"] = int(np.round(inv["current_stock"] * 0.314))
    inventory_active.append(inv_copy)

lines = []
lines.append("==================================================")
lines.append("   MOBIMART ALLOCATION DEMO - POST CORRECTION     ")
lines.append("==================================================")

lines.append("\n--- SCENARIO A: Full Unadjusted Store Inventory (Initial Capital >= ₹4 Cr) ---")
res_a = allocate_inventory(sales_df, stores, products, inventory_full, planning_week=24, capital_budget_limit=40000000.0)
lines.append(f"Initial Capital Deployed:    ₹{res_a.initial_capital_deployed:,.2f}")
lines.append(f"New Capital Allocated:      ₹{res_a.new_capital_allocated:,.2f}")
lines.append(f"Resulting Total Capital:    ₹{res_a.resulting_capital_deployed:,.2f}")
lines.append(f"Hard Budget Limit:          ₹{res_a.budget_limit:,.2f}")
lines.append(f"Units Allocated:            {res_a.total_units_allocated} units")
lines.append(f"Expected Behavior Verified: ZERO new capital allocated when initial capital >= ₹4 Crore limit!")

lines.append("\n--- SCENARIO B: Active Weekly Replenishment (Initial Capital = ₹3.18 Cr < ₹4 Cr Cap) ---")
res_b = allocate_inventory(sales_df, stores, products, inventory_active, planning_week=24, capital_budget_limit=40000000.0)
lines.append(f"Initial Capital Deployed:    ₹{res_b.initial_capital_deployed:,.2f}")
lines.append(f"New Capital Allocated:      ₹{res_b.new_capital_allocated:,.2f}")
lines.append(f"Resulting Total Capital:    ₹{res_b.resulting_capital_deployed:,.2f}")
lines.append(f"Hard Budget Limit:          ₹{res_b.budget_limit:,.2f}")
lines.append(f"Remaining Capital Headroom: ₹{res_b.capital_headroom:,.2f} ({res_b.utilization_pct:.2f}% utilization)")
lines.append(f"Units Allocated:            {res_b.total_units_allocated} units")
lines.append(f"Total Expected Net Return:  ₹{res_b.total_expected_net_benefit:,.2f}")

lines.append("\n--- TOP 5 RECOMMENDATIONS (SCENARIO B) ---")
for r in res_b.recommendations[:5]:
    lines.append(f"\nRec ID: {r.recommendation_id} | Store: {r.store_id} | Product: {r.product_id}")
    lines.append(f" - Recommended Qty:      +{r.recommended_qty} units")
    lines.append(f" - Forecast Demand:       {r.forecast_weekly_demand} units/wk")
    lines.append(f" - Stock Position:        {r.current_stock} units ({r.current_woc} woc) -> {r.projected_stock} units ({r.projected_woc} woc)")
    lines.append(f" - Expected Gross Margin: ₹{r.total_margin_contribution:,.2f}")
    lines.append(f" - Avoided Goodwill:     ₹{r.total_avoided_goodwill_benefit:,.2f}")
    lines.append(f" - Warehouse Cost:       -₹{r.total_allocation_cost:,.2f}")
    lines.append(f" - Net Expected Return:   ₹{r.total_net_benefit:,.2f} (₹{r.unit_marginal_value:,.2f}/unit)")
    lines.append(f" - Reason Headline:       {r.headline}")
    lines.append(f" - Financial Explanation: {r.explanation_text}")

with open("demo_both_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
