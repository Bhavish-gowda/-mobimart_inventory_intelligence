"""
Data Quality Report Generator for MobiMart Synthetic Dataset.
Generates comprehensive summary statistics proving realism, store differences,
festive uplift, successor cannibalization, and inventory capital deployment.
"""

from typing import Dict, Any
import pandas as pd
from backend.engine.generator.generator import generate_complete_dataset

def generate_quality_report() -> Dict[str, Any]:
    """
    Generate and print data quality report from synthetic dataset.
    """
    data = generate_complete_dataset()
    stores = data["stores"]
    products = data["products"]
    sales = data["sales_history"]
    inventory = data["inventory"]

    print("==================================================")
    print("      MOBIMART DATA QUALITY & REALISM REPORT      ")
    print("==================================================")

    # 1. Row counts & core scale
    store_count = len(stores)
    prod_count = len(products)
    sales_rows = len(sales)
    print(f"\n1. DATASET SCALE:")
    print(f"   - Store Count:             {store_count} stores (8 Bangalore, 17 Tier-2/3)")
    print(f"   - Product Count:           {prod_count} smartphone SKUs")
    print(f"   - Sales History Rows:      {sales_rows:,} (25 stores x 60 products x 52 weeks)")

    # 2. Total sales & revenue metrics
    total_units = sales["units_sold"].sum()
    total_revenue = sales["revenue"].sum()
    avg_weekly_sales = sales.groupby("week_number")["units_sold"].sum().mean()
    print(f"\n2. SALES PERFORMANCE:")
    print(f"   - 52-Week Total Units Sold: {total_units:,} units")
    print(f"   - 52-Week Total Revenue:    ₹{total_revenue:,.2f}")
    print(f"   - Avg Weekly Chain Demand:  {avg_weekly_sales:,.1f} units/week")

    # 3. Sales & ASP by City
    sales_merged = sales.merge(stores[["id", "city"]], left_on="store_id", right_on="id")
    city_summary = sales_merged.groupby("city").agg(
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum"),
    ).reset_index()
    city_summary["asp"] = city_summary["total_revenue"] / city_summary["total_units"]

    print(f"\n3. CITY DEMAND & ASP DISTRIBUTION:")
    for _, row in city_summary.iterrows():
        print(f"   - {row['city']:<12}: Units = {row['total_units']:>6,}, Revenue = ₹{row['total_revenue']:>12,.2f}, ASP = ₹{row['asp']:>9,.2f}")

    # 4. Sales by Product Segment
    sales_prod_merged = sales.merge(products[["id", "segment"]], left_on="product_id", right_on="id")
    segment_summary = sales_prod_merged.groupby("segment").agg(
        total_units=("units_sold", "sum"),
        total_revenue=("revenue", "sum"),
    ).reset_index()
    print(f"\n4. PRODUCT SEGMENT DISTRIBUTION:")
    for _, row in segment_summary.iterrows():
        print(f"   - {row['segment']:<10}: Units = {row['total_units']:>6,}, Revenue = ₹{row['total_revenue']:>12,.2f}")

    # 5. Festive Uplift Ratio (Diwali W42 vs Baseline W20)
    w20_sales = sales[sales["week_number"] == 20]["units_sold"].sum()
    w42_sales = sales[sales["week_number"] == 42]["units_sold"].sum()
    festive_uplift = (w42_sales / max(1, w20_sales))
    print(f"\n5. FESTIVE UPLIFT EFFECT:")
    print(f"   - Week 20 (Normal Week) Sales:  {w20_sales:,} units")
    print(f"   - Week 42 (Diwali Week) Sales:   {w42_sales:,} units")
    print(f"   - Diwali Demand Uplift Ratio:    {festive_uplift:.2f}x multiplier")

    # 6. Successor Cannibalization Effect
    # Predecessor Apex Note 11 (PROD_019) vs Successor Apex Note 12 (PROD_020 launched week 18)
    pred_sales_pre = sales[(sales["product_id"] == "PROD_019") & (sales["week_number"] < 18)]["units_sold"].mean()
    pred_sales_post = sales[(sales["product_id"] == "PROD_019") & (sales["week_number"] >= 25)]["units_sold"].mean()
    print(f"\n6. SUCCESSOR CANNIBALIZATION EFFECT:")
    print(f"   - Predecessor PROD_019 (Apex Note 11) Avg Sales Pre-Successor (W1-17): {pred_sales_pre:.1f} units/wk")
    print(f"   - Predecessor PROD_019 (Apex Note 11) Avg Sales Post-Successor (W25-52): {pred_sales_post:.1f} units/wk")
    print(f"   - Demand Decay Percentage: {((pred_sales_pre - pred_sales_post) / pred_sales_pre * 100):.1f}% reduction")

    # 7. Lifecycle Distribution
    lifecycle_counts = products["lifecycle_stage"].value_counts().to_dict()
    print(f"\n7. PRODUCT LIFECYCLE DISTRIBUTION:")
    for stage, count in lifecycle_counts.items():
        print(f"   - {stage:<10}: {count} SKUs")

    # 8. Initial Inventory Capital
    total_inv_capital = inventory["capital_allocated"].sum()
    total_inv_units = inventory["current_stock"].sum()
    print(f"\n8. INITIAL INVENTORY CAPITAL STATE (WEEK 0):")
    print(f"   - Total Inventory Units:   {total_inv_units:,} units across 25 stores")
    print(f"   - Total Inventory Capital: ₹{total_inv_capital:,.2f}")
    print(f"==================================================\n")

    return {
        "store_count": store_count,
        "product_count": prod_count,
        "sales_rows": sales_rows,
        "total_revenue": total_revenue,
        "total_units": total_units,
        "festive_uplift": festive_uplift,
        "total_inv_capital": total_inv_capital,
    }

if __name__ == "__main__":
    generate_quality_report()
