"""
Data Audit Script for MobiMart Synthetic Dataset.
Calculates exact mathematical metrics across all 12 evaluation categories.
"""

import pandas as pd
import numpy as np

def run_audit():
    stores = pd.read_csv("data/generated/stores.csv")
    products = pd.read_csv("data/generated/products.csv")
    sales = pd.read_csv("data/generated/sales_history.csv")
    inventory = pd.read_csv("data/generated/inventory.csv")
    events = pd.read_csv("data/generated/product_events.csv")

    sales_m = sales.merge(stores, left_on="store_id", right_on="id")
    sales_m = sales_m.merge(products, left_on="product_id", right_on="id")

    print("==================================================")
    print("         MOBIMART DATA AUDIT RESULTS              ")
    print("==================================================")

    # 1. STORE SALES DISTRIBUTION
    store_stats = sales_m.groupby(["store_id", "name", "city"]).agg(
        total_units=("units_sold", "sum"),
        avg_weekly_units=("units_sold", lambda x: x.sum() / 52.0),
        total_revenue=("revenue", "sum"),
    ).reset_index()

    store_stats["asp"] = store_stats["total_revenue"] / store_stats["total_units"]

    # Calculate segment mix per store
    seg_mix = sales_m.groupby(["store_id", "segment"])["units_sold"].sum().unstack(fill_value=0)
    seg_mix_pct = seg_mix.div(seg_mix.sum(axis=1), axis=0) * 100

    store_full = store_stats.merge(seg_mix_pct, on="store_id").sort_values(by="total_units", ascending=False)

    print("\n--- 1. STORE SALES DISTRIBUTION (Sorted by Total Annual Units) ---")
    for _, r in store_full.iterrows():
        print(f"{r['store_id']} | {r['name']:<32} | {r['city']:<10} | Units: {r['total_units']:>5} | Wkly: {r['avg_weekly_units']:>5.1f} | Rev: ₹{r['total_revenue']:>11,.2f} | ASP: ₹{r['asp']:>8,.2f} | Mix: Bud={r.get('Budget',0):>4.1f}% Mid={r.get('Mid-Range',0):>4.1f}% Prem={r.get('Premium',0):>4.1f}% Flag={r.get('Flagship',0):>4.1f}%")

    top_vol = store_full.iloc[0]
    low_vol = store_full.iloc[-1]
    top_asp = store_full.sort_values(by="asp", ascending=False).iloc[0]
    low_asp = store_full.sort_values(by="asp", ascending=True).iloc[0]

    print(f"\nHighest Volume Store: {top_vol['name']} ({top_vol['total_units']} units)")
    print(f"Lowest Volume Store:  {low_vol['name']} ({low_vol['total_units']} units)")
    print(f"Highest ASP Store:    {top_asp['name']} (ASP ₹{top_asp['asp']:,.2f})")
    print(f"Lowest ASP Store:     {low_asp['name']} (ASP ₹{low_asp['asp']:,.2f})")

    # 2. CITY-LEVEL DISTRIBUTION
    city_stats = sales_m.groupby("city").agg(
        store_count=("store_id", "nunique"),
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum"),
        avg_weekly_units=("units_sold", lambda x: x.sum() / 52.0),
    ).reset_index()
    city_stats["asp"] = city_stats["total_revenue"] / city_stats["total_units"]

    city_seg_mix = sales_m.groupby(["city", "segment"])["units_sold"].sum().unstack(fill_value=0)
    city_seg_pct = city_seg_mix.div(city_seg_mix.sum(axis=1), axis=0) * 100
    city_full = city_stats.merge(city_seg_pct, on="city").sort_values(by="total_revenue", ascending=False)

    print("\n--- 2. CITY-LEVEL DISTRIBUTION ---")
    for _, r in city_full.iterrows():
        print(f"{r['city']:<12} | Stores: {r['store_count']} | Units: {r['total_units']:>6,} | Wkly: {r['avg_weekly_units']:>6.1f} | Rev: ₹{r['total_revenue']:>12,.2f} | ASP: ₹{r['asp']:>8,.2f} | Mix: Bud={r.get('Budget',0):>4.1f}% Mid={r.get('Mid-Range',0):>4.1f}% Prem={r.get('Premium',0):>4.1f}% Flag={r.get('Flagship',0):>4.1f}%")

    # 3. PRODUCT DISTRIBUTION
    prod_stats = sales_m.groupby(["product_id", "model_name", "segment", "lifecycle_stage"]).agg(
        total_units=("units_sold", "sum"),
        avg_weekly_units=("units_sold", lambda x: x.sum() / 52.0),
        total_revenue=("revenue", "sum"),
    ).reset_index()
    prod_stats["asp"] = prod_stats["total_revenue"] / np.maximum(1, prod_stats["total_units"])

    prod_inv = inventory.groupby("product_id").agg(
        current_inventory=("current_stock", "sum"),
        inventory_value=("capital_allocated", "sum"),
    ).reset_index()

    prod_full = prod_stats.merge(prod_inv, left_on="product_id", right_on="product_id")
    prod_full["weeks_of_cover"] = prod_full["current_inventory"] / np.maximum(0.1, prod_full["avg_weekly_units"])

    print("\n--- 3. PRODUCT DISTRIBUTION HIGHLIGHTS ---")
    print("\nTop 10 Products by Units:")
    print(prod_full.sort_values(by="total_units", ascending=False)[["product_id", "model_name", "segment", "total_units", "total_revenue", "weeks_of_cover"]].head(10).to_string(index=False))

    print("\nBottom 10 Products by Units:")
    print(prod_full.sort_values(by="total_units", ascending=True)[["product_id", "model_name", "segment", "total_units", "total_revenue", "weeks_of_cover"]].head(10).to_string(index=False))

    print("\nTop 10 Products by Inventory Value:")
    print(prod_full.sort_values(by="inventory_value", ascending=False)[["product_id", "model_name", "segment", "current_inventory", "inventory_value", "weeks_of_cover"]].head(10).to_string(index=False))

    print("\nTop 10 Products by Weeks of Cover:")
    print(prod_full.sort_values(by="weeks_of_cover", ascending=False)[["product_id", "model_name", "segment", "lifecycle_stage", "current_inventory", "avg_weekly_units", "weeks_of_cover"]].head(10).to_string(index=False))

    # 4. SEGMENT DISTRIBUTION
    seg_summary = sales_m.groupby("segment").agg(
        product_count=("product_id", "nunique"),
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum"),
    ).reset_index()

    total_units_all = seg_summary["total_units"].sum()
    total_rev_all = seg_summary["total_revenue"].sum()
    seg_summary["pct_units"] = (seg_summary["total_units"] / total_units_all) * 100
    seg_summary["pct_revenue"] = (seg_summary["total_revenue"] / total_rev_all) * 100
    seg_summary["avg_asp"] = seg_summary["total_revenue"] / seg_summary["total_units"]

    seg_inv = prod_full.groupby("segment").agg(
        total_inv_units=("current_inventory", "sum"),
        total_inv_val=("inventory_value", "sum"),
        avg_weekly_units=("avg_weekly_units", "sum"),
    ).reset_index()
    seg_inv["avg_woc"] = seg_inv["total_inv_units"] / seg_inv["avg_weekly_units"]

    seg_full = seg_summary.merge(seg_inv[["segment", "avg_woc", "total_inv_val"]], on="segment")

    print("\n--- 4. SEGMENT DISTRIBUTION ---")
    for _, r in seg_full.iterrows():
        print(f"{r['segment']:<10} | SKUs: {r['product_count']:>2} | Units: {r['total_units']:>6,} ({r['pct_units']:>4.1f}%) | Rev: ₹{r['total_revenue']:>12,.2f} ({r['pct_revenue']:>4.1f}%) | ASP: ₹{r['avg_asp']:>8,.2f} | Avg WoC: {r['avg_woc']:>4.1f} wks")

    # 5. FESTIVE AUDIT
    w_normal = sales_m[sales_m["week_number"].isin([15, 16, 17, 18, 19, 20])].groupby("week_number")["units_sold"].sum().mean()
    w_normal_rev = sales_m[sales_m["week_number"].isin([15, 16, 17, 18, 19, 20])].groupby("week_number")["revenue"].sum().mean()

    w_dussehra = sales_m[sales_m["week_number"] == 41]["units_sold"].sum()
    w_dussehra_rev = sales_m[sales_m["week_number"] == 41]["revenue"].sum()

    w_diwali = sales_m[sales_m["week_number"] == 42]["units_sold"].sum()
    w_diwali_rev = sales_m[sales_m["week_number"] == 42]["revenue"].sum()

    w_ny = sales_m[sales_m["week_number"] == 52]["units_sold"].sum()
    w_ny_rev = sales_m[sales_m["week_number"] == 52]["revenue"].sum()

    print("\n--- 5. FESTIVE AUDIT ---")
    print(f"Normal Week Avg: Units = {w_normal:,.1f}, Rev = ₹{w_normal_rev:,.2f}")
    print(f"Dussehra (W41):  Units = {w_dussehra:,.0f}, Rev = ₹{w_dussehra_rev:,.2f}, Uplift = {w_dussehra / w_normal:.2f}x")
    print(f"Diwali (W42):    Units = {w_diwali:,.0f}, Rev = ₹{w_diwali_rev:,.2f}, Uplift = {w_diwali / w_normal:.2f}x")
    print(f"New Year (W52):  Units = {w_ny:,.0f}, Rev = ₹{w_ny_rev:,.2f}, Uplift = {w_ny / w_normal:.2f}x")

    # Segment festive uplift (Diwali W42 vs Normal W20)
    w20_seg = sales_m[sales_m["week_number"] == 20].groupby("segment")["units_sold"].sum()
    w42_seg = sales_m[sales_m["week_number"] == 42].groupby("segment")["units_sold"].sum()
    festive_seg_df = pd.DataFrame({"Normal_W20": w20_seg, "Diwali_W42": w42_seg})
    festive_seg_df["Uplift_Ratio"] = festive_seg_df["Diwali_W42"] / festive_seg_df["Normal_W20"]
    print("\nFestive Uplift by Segment (Diwali W42 vs Normal W20):")
    print(festive_seg_df.to_string())

    # 6. SUCCESSOR CANNIBALIZATION AUDIT
    pred_succ_list = products.dropna(subset=["successor_product_id"])[["id", "model_name", "successor_product_id", "expected_successor_week", "is_rumoured", "launch_confidence"]]
    
    cannibalization_results = []
    for _, row in pred_succ_list.iterrows():
        pid = row["id"]
        sid = row["successor_product_id"]
        succ_wk = row["expected_successor_week"]
        s_name = products[products["id"] == sid]["model_name"].iloc[0]

        pred_pre = sales[sales["product_id"] == pid][sales["week_number"] < succ_wk]["units_sold"].mean()
        pred_post = sales[sales["product_id"] == pid][sales["week_number"] >= succ_wk + 4]["units_sold"].mean()
        pct_change = ((pred_post - pred_pre) / pred_pre) * 100 if pred_pre > 0 else 0.0

        succ_pre = sales[sales["product_id"] == sid][sales["week_number"] < succ_wk]["units_sold"].mean()
        succ_post = sales[sales["product_id"] == sid][sales["week_number"] >= succ_wk]["units_sold"].mean()

        cannibalization_results.append({
            "Predecessor": f"{pid} ({row['model_name']})",
            "Successor": f"{sid} ({s_name})",
            "Launch_Wk": succ_wk,
            "Pred_Pre_Sales": round(pred_pre, 2),
            "Pred_Post_Sales": round(pred_post, 2),
            "Decay_Pct": round(pct_change, 1),
            "Succ_Pre_Sales": round(succ_pre, 2),
            "Succ_Post_Sales": round(succ_post, 2),
        })

    cann_df = pd.DataFrame(cannibalization_results).sort_values(by="Decay_Pct", ascending=True)
    print("\n--- 6. SUCCESSOR CANNIBALIZATION AUDIT (Top Pairs) ---")
    print(cann_df.head(10).to_string(index=False))

    # 7. LIFECYCLE AUDIT
    lc_summary = prod_full.groupby("lifecycle_stage").agg(
        product_count=("product_id", "count"),
        inventory_units=("current_inventory", "sum"),
        inventory_capital=("inventory_value", "sum"),
    ).reset_index()

    print("\n--- 7. LIFECYCLE AUDIT ---")
    print(lc_summary.to_string(index=False))

    # 8. INVENTORY AUDIT
    tot_inv_units = inventory["current_stock"].sum()
    tot_inv_cost = inventory["capital_allocated"].sum()
    inventory_m = inventory.merge(products[["id", "retail_price"]], left_on="product_id", right_on="id")
    tot_inv_retail = (inventory_m["current_stock"] * inventory_m["retail_price"]).sum()

    cap_limit = 40000000.00
    headroom = cap_limit - tot_inv_cost
    pct_deployed = (tot_inv_cost / cap_limit) * 100

    print("\n--- 8. INVENTORY AUDIT ---")
    print(f"Total Inventory Units:        {tot_inv_units:,} units")
    print(f"Total Inventory Cost Value:   ₹{tot_inv_cost:,.2f}")
    print(f"Total Inventory Retail Value: ₹{tot_inv_retail:,.2f}")
    print(f"₹4 Crore Budget Limit:        ₹{cap_limit:,.2f}")
    print(f"Available Headroom:           ₹{headroom:,.2f}")
    print(f"Percentage Deployed:          {pct_deployed:.2f}%")

    # 9. DEMAND VS SALES FIELD INSPECTION
    print("\n--- 9. FIELD INSPECTION (sales_history) ---")
    print(sales[["week_number", "store_id", "product_id", "demand_units", "units_sold", "lost_sales_estimated", "stockout_flag"]].head(10).to_string(index=False))

    # 10. RANDOMNESS & REALISM AUDIT
    weekly_store_sales = sales.groupby(["store_id", "week_number"])["units_sold"].sum()
    cv_weekly_store = weekly_store_sales.std() / weekly_store_sales.mean()

    zero_sales_combos = (sales["units_sold"] == 0).sum()
    pct_zero_sales = (zero_sales_combos / len(sales)) * 100

    print("\n--- 10. REALISM & VARIATION METRICS ---")
    print(f"Weekly Store Sales Coeff of Variation (CV): {cv_weekly_store:.3f}")
    print(f"Zero Sales Combinations:                   {zero_sales_combos:,} ({pct_zero_sales:.2f}%)")

if __name__ == "__main__":
    run_audit()
