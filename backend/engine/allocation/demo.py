"""
Command-Line Development & Defense Demo Runner for Allocation Engine.
Executes Monday allocation run for Week 24 under ₹4 Crore budget limit.
Displays initial capital, recommendations, rupee proofs, and resulting capital headroom.
"""

import pandas as pd
from backend.engine.allocation.allocator import allocate_inventory

def run_demo():
    print("==================================================")
    print("   MOBIMART ALLOCATION ENGINE INTERVIEW DEMO      ")
    print("==================================================")

    # Load synthetic dataset
    stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
    products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
    sales_df = pd.read_csv("data/generated/sales_history.csv")
    inventory = pd.read_csv("data/generated/inventory.csv").to_dict(orient="records")

    planning_week = 24

    print(f"\nExecuting Monday Allocation Run for Week {planning_week}...")
    run_result = allocate_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory,
        planning_week=planning_week,
        capital_budget_limit=40000000.0,  # ₹4 Crore Limit
    )

    print("\n--- 1. CAPITAL BUDGET SUMMARY ---")
    print(f"Initial Deployed Capital:   ₹{run_result.initial_capital_deployed:,.2f}")
    print(f"New Capital Allocated:     ₹{run_result.new_capital_allocated:,.2f}")
    print(f"Resulting Total Capital:   ₹{run_result.resulting_capital_deployed:,.2f}")
    print(f"Hard Budget Limit:         ₹{run_result.budget_limit:,.2f}")
    print(f"Remaining Capital Headroom: ₹{run_result.capital_headroom:,.2f}")
    print(f"Budget Utilization:        {run_result.utilization_pct:.2f}%")
    print(f"Total Units Allocated:     {run_result.total_units_allocated} units")
    print(f"Total Expected Net Return: ₹{run_result.total_expected_net_benefit:,.2f}")

    print("\n--- 2. TOP 8 ALLOCATION RECOMMENDATIONS ---")
    for rec in run_result.recommendations[:8]:
        print(f"\nRec ID: {rec.recommendation_id} | Store: {rec.store_id} | Product: {rec.product_id}")
        print(f" - Quantity Recommended:  +{rec.recommended_qty} units")
        print(f" - Forecast Weekly Demand: {rec.forecast_weekly_demand} units/wk")
        print(f" - Stock Position:        {rec.current_stock} units ({rec.current_woc} woc) -> {rec.projected_stock} units ({rec.projected_woc} woc)")
        print(f" - Avoided Stockout Loss:  ₹{rec.total_avoided_stockout_loss:,.2f}")
        print(f" - Expected Margin:        ₹{rec.total_margin_contribution:,.2f}")
        print(f" - Logistics Fee:          -₹{rec.total_allocation_cost:,.2f}")
        print(f" - Net Expected Return:    ₹{rec.total_net_benefit:,.2f} (₹{rec.unit_marginal_value:,.2f}/unit)")
        print(f" - Reason Headline:        {rec.headline}")
        print(f" - Explanation:            {rec.explanation_text}")

    print("\n==================================================")

if __name__ == "__main__":
    run_demo()
