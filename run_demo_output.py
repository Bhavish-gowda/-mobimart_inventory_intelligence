import io
import sys
from backend.engine.allocation.allocator import allocate_inventory
import pandas as pd

stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
sales_df = pd.read_csv("data/generated/sales_history.csv")
inventory = pd.read_csv("data/generated/inventory.csv").to_dict(orient="records")

res = allocate_inventory(sales_df, stores, products, inventory, planning_week=24, capital_budget_limit=40000000.0)

print(f"INITIAL CAPITAL: ₹{res.initial_capital_deployed:,.2f}")
print(f"NEW ALLOCATED CAPITAL: ₹{res.new_capital_allocated:,.2f}")
print(f"RESULTING CAPITAL: ₹{res.resulting_capital_deployed:,.2f}")
print(f"HEADROOM: ₹{res.capital_headroom:,.2f} ({res.utilization_pct:.2f}% utilization)")
print(f"UNITS ALLOCATED: {res.total_units_allocated} units")
print(f"NET FINANCIAL BENEFIT: ₹{res.total_expected_net_benefit:,.2f}")

print("\n--- TOP 5 RECOMMENDATIONS ---")
for r in res.recommendations[:5]:
    print(f"Rec {r.recommendation_id} | Store {r.store_id} | Prod {r.product_id} | Qty +{r.recommended_qty} | Net ₹{r.total_net_benefit:,.2f} | Margin ₹{r.total_margin_contribution:,.2f} | Goodwill ₹{r.total_avoided_goodwill_benefit:,.2f} | Cost -₹{r.total_allocation_cost:,.2f}")
    print(f"Explanation: {r.explanation_text}\n")
