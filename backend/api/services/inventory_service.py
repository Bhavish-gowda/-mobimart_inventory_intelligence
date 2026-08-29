"""
Inventory Service Layer.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.api.data_loader import load_inventory_list, load_stores_list, load_products_list, load_sales_history_df
from backend.engine.simulation.state import build_starting_inventory_snapshot

def get_inventory_records(
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    records = load_inventory_list()
    filtered = []

    for r in records:
        if store_id and r.get("store_id") != store_id:
            continue
        if product_id and r.get("product_id") != product_id:
            continue
        filtered.append(r)

    total_count = len(filtered)
    if page is not None and page_size is not None and page > 0 and page_size > 0:
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        filtered = filtered[start_idx:end_idx]

    return filtered, total_count

def get_inventory_summary() -> Dict[str, Any]:
    inventory_records = load_inventory_list()
    stores = load_stores_list()
    products = load_products_list()
    products_by_id = {p["id"]: p for p in products}

    snapshot = build_starting_inventory_snapshot(
        inventory_records,
        products,
        stores,
        target_capital=38000000.0,
    )

    total_units = sum(int(r.get("current_stock", 0)) for r in inventory_records)
    total_retail_val = sum(
        int(r.get("current_stock", 0)) * float(products_by_id.get(r["product_id"], {}).get("retail_price", 0.0))
        for r in inventory_records
    )

    cap_limit = 40000000.0
    utilization_pct = (snapshot.operational_inventory_cost / cap_limit) * 100.0

    # 4-Week Telemetry (Weeks 1 to 4)
    sales_df = load_sales_history_df()
    w1_4 = sales_df[(sales_df["week_number"] >= 1) & (sales_df["week_number"] <= 4)]
    units_sold_4w = int(w1_4["units_sold"].sum())
    demand_units_4w = int(w1_4["demand_units"].sum())
    revenue_4w = float(w1_4["revenue"].sum())
    cogs_4w = sum(row["units_sold"] * float(products_by_id.get(row["product_id"], {}).get("cost_price", 0.0)) for _, row in w1_4.iterrows())
    margin_4w = revenue_4w - cogs_4w
    fill_rate_4w = (units_sold_4w / float(demand_units_4w) * 100.0) if demand_units_4w > 0 else 0.0

    return {
        "total_units": total_units,
        "raw_cost_value": snapshot.raw_inventory_cost,
        "operational_cost_value": snapshot.operational_inventory_cost,
        "total_retail_value": round(total_retail_val, 2),
        "store_count": len(stores),
        "sku_count": len(products),
        "capital_budget_limit": cap_limit,
        "capital_headroom": snapshot.capital_headroom,
        "capital_utilization_pct": round(utilization_pct, 2),
        "four_week_sales_units": units_sold_4w,
        "four_week_demand_units": demand_units_4w,
        "four_week_revenue": round(revenue_4w, 2),
        "four_week_margin": round(margin_4w, 2),
        "four_week_fill_rate": round(fill_rate_4w, 2),
    }
