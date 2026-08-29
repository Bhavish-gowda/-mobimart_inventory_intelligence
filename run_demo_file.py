import pandas as pd
from backend.engine.allocation.allocator import allocate_inventory

stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
sales_df = pd.read_csv("data/generated/sales_history.csv")
inventory = pd.read_csv("data/generated/inventory.csv").to_dict(orient="records")

res = allocate_inventory(sales_df, stores, products, inventory, planning_week=24, capital_budget_limit=40000000.0)

with open("demo_results.txt", "w", encoding="utf-8") as f:
    f.write(f"INITIAL CAPITAL: ₹{res.initial_capital_deployed:,.2f}\n")
    f.write(f"NEW ALLOCATED CAPITAL: ₹{res.new_capital_allocated:,.2f}\n")
    f.write(f"RESULTING CAPITAL: ₹{res.resulting_capital_deployed:,.2f}\n")
    f.write(f"HEADROOM: ₹{res.capital_headroom:,.2f} ({res.utilization_pct:.2f}% utilization)\n")
    f.write(f"UNITS ALLOCATED: {res.total_units_allocated} units\n")
    f.write(f"NET FINANCIAL BENEFIT: ₹{res.total_expected_net_benefit:,.2f}\n\n")

    f.write("--- TOP 5 RECOMMENDATIONS ---\n")
    for r in res.recommendations[:5]:
        f.write(f"Rec {r.recommendation_id} | Store {r.store_id} | Prod {r.product_id} | Qty +{r.recommended_qty} | Net ₹{r.total_net_benefit:,.2f} | Margin ₹{r.total_margin_contribution:,.2f} | Goodwill ₹{r.total_avoided_goodwill_benefit:,.2f} | Cost -₹{r.total_allocation_cost:,.2f}\n")
        f.write(f"Explanation: {r.explanation_text}\n\n")
