"""
Master Synthetic Data Generator for MobiMart.
Coordinates store generation, product lifecycle generation, weekly causal sales history simulation,
and initial inventory state creation. Exports data to CSV files in data/generated/.
"""

import os
from typing import Dict, List, Any, Tuple
import numpy as np
import pandas as pd

from backend.engine.generator.config import RANDOM_SEED, NUM_STORES, NUM_PRODUCTS, NUM_WEEKS
from backend.engine.generator.stores import generate_stores
from backend.engine.generator.products import generate_products
from backend.engine.generator.demand import calculate_weekly_demand
from backend.engine.generator.inventory import generate_initial_inventory

def generate_complete_dataset(
    seed: int = RANDOM_SEED,
    output_dir: str = "data/generated"
) -> Dict[str, pd.DataFrame]:
    """
    Generate complete MobiMart synthetic dataset.
    Returns dictionary of DataFrames and exports CSV files to output_dir.
    """
    rng = np.random.default_rng(seed)

    # 1. Generate Stores (25)
    stores = generate_stores(rng)
    stores_df = pd.DataFrame(stores)

    # 2. Generate Products (60)
    products = generate_products(rng)
    products_df = pd.DataFrame(products)

    all_products_by_id = {p["id"]: p for p in products}

    # 3. Simulate 52 Weeks Sales History & Demand
    sales_records: List[Dict[str, Any]] = []
    store_prod_demand_sum: Dict[Tuple[str, str], float] = {}

    for week in range(1, NUM_WEEKS + 1):
        for store in stores:
            for product in products:
                # Calculate weekly causal demand
                raw_demand = calculate_weekly_demand(
                    store, product, week, all_products_by_id, rng
                )
                
                # Integer units demanded
                demand_units = int(np.round(raw_demand))

                # For simulation of historical fulfillment:
                # In historical sales, assume ~92% average stock fulfillment rate with mild stockout noise
                if demand_units == 0:
                    units_sold = 0
                    lost_sales = 0
                    stockout_flag = False
                else:
                    fulfillment_prob = float(rng.uniform(0.85, 0.98))
                    units_sold = int(np.round(demand_units * fulfillment_prob))
                    lost_sales = demand_units - units_sold
                    stockout_flag = lost_sales > 0

                revenue = round(units_sold * product["retail_price"], 2)

                sales_entry = {
                    "week_number": week,
                    "store_id": store["id"],
                    "product_id": product["id"],
                    "demand_units": demand_units,
                    "units_sold": units_sold,
                    "lost_sales_estimated": lost_sales,
                    "stockout_flag": stockout_flag,
                    "revenue": revenue,
                    "retail_price": product["retail_price"],
                    "cost_price": product["cost_price"],
                }
                sales_records.append(sales_entry)

                # Accumulate for average weekly demand calculation
                key = (store["id"], product["id"])
                store_prod_demand_sum[key] = store_prod_demand_sum.get(key, 0.0) + demand_units

    sales_df = pd.DataFrame(sales_records)

    # Calculate average weekly demand per (store, product)
    avg_weekly_demand = {
        k: v / float(NUM_WEEKS) for k, v in store_prod_demand_sum.items()
    }

    # 4. Generate Initial Inventory State (Week 0)
    inventory = generate_initial_inventory(stores, products, avg_weekly_demand, rng)
    inventory_df = pd.DataFrame(inventory)

    # 5. Generate Product Events Log (Successor launches, festive events)
    events: List[Dict[str, Any]] = []
    for p in products:
        if p.get("successor_product_id") and p.get("expected_successor_week"):
            events.append({
                "product_id": p["id"],
                "event_type": "Successor_Launch",
                "target_product_id": p["successor_product_id"],
                "week_number": p["expected_successor_week"],
                "is_rumoured": p["is_rumoured"],
                "launch_confidence": p["launch_confidence"],
                "description": f"Successor {p['successor_product_id']} launch scheduled for week {p['expected_successor_week']}",
            })

    events_df = pd.DataFrame(events)

    # Export to CSV if output_dir provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        stores_df.to_csv(os.path.join(output_dir, "stores.csv"), index=False)
        products_df.to_csv(os.path.join(output_dir, "products.csv"), index=False)
        sales_df.to_csv(os.path.join(output_dir, "sales_history.csv"), index=False)
        inventory_df.to_csv(os.path.join(output_dir, "inventory.csv"), index=False)
        events_df.to_csv(os.path.join(output_dir, "product_events.csv"), index=False)

    return {
        "stores": stores_df,
        "products": products_df,
        "sales_history": sales_df,
        "inventory": inventory_df,
        "product_events": events_df,
    }

if __name__ == "__main__":
    datasets = generate_complete_dataset()
    print("Dataset generation complete!")
    for name, df in datasets.items():
        print(f" - {name}: {len(df)} rows")
