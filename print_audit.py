import pandas as pd
import numpy as np

stores = pd.read_csv("data/generated/stores.csv")
products = pd.read_csv("data/generated/products.csv")
sales = pd.read_csv("data/generated/sales_history.csv")
inventory = pd.read_csv("data/generated/inventory.csv")

sales_m = sales.merge(stores, left_on="store_id", right_on="id").merge(products, left_on="product_id", right_on="id")

print("=== 1. STORE STATS ===")
store_stats = sales_m.groupby(["store_id", "name", "city"]).agg(
    total_units=("units_sold", "sum"),
    avg_weekly_units=("units_sold", lambda x: x.sum() / 52.0),
    total_revenue=("revenue", "sum"),
).reset_index()
store_stats["asp"] = store_stats["total_revenue"] / store_stats["total_units"]

seg_mix = sales_m.groupby(["store_id", "segment"])["units_sold"].sum().unstack(fill_value=0)
seg_pct = seg_mix.div(seg_mix.sum(axis=1), axis=0) * 100

store_full = store_stats.merge(seg_pct, on="store_id").sort_values(by="total_units", ascending=False)

for _, r in store_full.iterrows():
    print(f"{r['store_id']} | {r['name'][:30]:<30} | {r['city']:<10} | Units: {r['total_units']:>5} | Wkly: {r['avg_weekly_units']:>5.1f} | Rev: ₹{r['total_revenue']:>11,.2f} | ASP: ₹{r['asp']:>8,.2f} | Bud:{r.get('Budget',0):>4.1f}% Mid:{r.get('Mid-Range',0):>4.1f}% Prem:{r.get('Premium',0):>4.1f}% Flag:{r.get('Flagship',0):>4.1f}%")

print("\n=== 2. CITY STATS ===")
city_stats = sales_m.groupby("city").agg(
    store_count=("store_id", "nunique"),
    total_units=("units_sold", "sum"),
    total_revenue=("revenue", "sum"),
).reset_index()
city_stats["asp"] = city_stats["total_revenue"] / city_stats["total_units"]

city_seg = sales_m.groupby(["city", "segment"])["units_sold"].sum().unstack(fill_value=0)
city_pct = city_seg.div(city_seg.sum(axis=1), axis=0) * 100
city_full = city_stats.merge(city_pct, on="city").sort_values(by="total_revenue", ascending=False)

for _, r in city_full.iterrows():
    print(f"{r['city']:<10} | Stores:{r['store_count']} | Units:{r['total_units']:>5} | Wkly:{r['total_units']/52:>5.1f} | Rev:₹{r['total_revenue']:>11,.2f} | ASP:₹{r['asp']:>8,.2f} | Bud:{r.get('Budget',0):>4.1f}% Mid:{r.get('Mid-Range',0):>4.1f}% Prem:{r.get('Premium',0):>4.1f}% Flag:{r.get('Flagship',0):>4.1f}%")

print("\n=== 4. SEGMENT STATS ===")
seg_sum = sales_m.groupby("segment").agg(
    skus=("product_id", "nunique"),
    units=("units_sold", "sum"),
    rev=("revenue", "sum"),
).reset_index()
seg_sum["asp"] = seg_sum["rev"] / seg_sum["units"]
seg_sum["pct_units"] = (seg_sum["units"] / seg_sum["units"].sum()) * 100
seg_sum["pct_rev"] = (seg_sum["rev"] / seg_sum["rev"].sum()) * 100
for _, r in seg_sum.iterrows():
    print(f"{r['segment']:<10} | SKUs:{r['skus']:>2} | Units:{r['units']:>5} ({r['pct_units']:>4.1f}%) | Rev:₹{r['rev']:>11,.2f} ({r['pct_rev']:>4.1f}%) | ASP:₹{r['asp']:>8,.2f}")
