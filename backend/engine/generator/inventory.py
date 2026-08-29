"""
Initial inventory state generator for MobiMart.
Calculates initial Week 0 inventory per store-product pair based on expected sales velocity,
store catchment, and lifecycle stage. Intentionally injects excess stock into EOL/Decline SKUs.
"""

from typing import Dict, List, Any, Tuple
import numpy as np

def generate_initial_inventory(
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    avg_weekly_demand: Dict[Tuple[str, str], float],
    rng: np.random.Generator,
) -> List[Dict[str, Any]]:
    """
    Generate initial inventory records for Week 0.
    """
    inventory_records: List[Dict[str, Any]] = []

    for store in stores:
        for product in products:
            key = (store["id"], product["id"])
            avg_demand = avg_weekly_demand.get(key, 0.5)

            stage = product["lifecycle_stage"]

            # Target weeks of cover based on lifecycle stage
            if stage in ["Launch", "Growth"]:
                target_woc = float(rng.uniform(3.0, 4.5))
            elif stage == "Peak":
                target_woc = float(rng.uniform(2.5, 3.5))
            elif stage == "Decline":
                target_woc = float(rng.uniform(4.5, 7.0))  # Higher cover due to slowing sales
            else:  # EOL
                target_woc = float(rng.uniform(6.0, 10.0)) # Intentionally excess stock!

            # Calculate target and initial stock
            target_stock = int(np.ceil(avg_demand * target_woc))
            
            # Initial stock fluctuates around target stock
            stock_ratio = float(rng.uniform(0.70, 1.25))
            current_stock = int(np.round(target_stock * stock_ratio))

            # Guarantee non-negative stock
            current_stock = max(0, current_stock)

            cost_price = product["cost_price"]
            capital_allocated = round(current_stock * cost_price, 2)

            inventory_entry = {
                "store_id": store["id"],
                "product_id": product["id"],
                "current_stock": current_stock,
                "in_transit_stock": 0,
                "reserved_stock": 0,
                "target_stock_level": target_stock,
                "reorder_point": max(2, int(np.ceil(target_stock * 0.4))),
                "capital_allocated": capital_allocated,
                "weeks_of_cover": round(current_stock / max(0.1, avg_demand), 2),
            }
            inventory_records.append(inventory_entry)

    return inventory_records
