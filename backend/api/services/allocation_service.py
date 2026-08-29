"""
Allocation Service Layer.
Delegates directly to Phase 3A constrained greedy allocator (`allocate_inventory`).
Does NOT duplicate allocation logic.
"""

from typing import Dict, List, Any, Optional
from backend.api.data_loader import (
    load_sales_history_df,
    load_stores_list,
    load_products_list,
    load_inventory_list,
)
from backend.engine.allocation.allocator import allocate_inventory
from backend.engine.allocation.models import AllocationRunResult

def run_allocation(
    planning_week: int,
    capital_budget_limit: float = 40000000.0,
    warehouse_available: Optional[Dict[str, int]] = None,
) -> AllocationRunResult:
    stores = load_stores_list()
    products = load_products_list()
    inventory_records = load_inventory_list()
    sales_df = load_sales_history_df()

    # Pass sales history up to planning_week (recent 12 weeks max needed for 6-week rolling avg & confidence) for zero future leakage
    start_wk = max(1, planning_week - 12)
    hist_df = sales_df[(sales_df["week_number"] >= start_wk) & (sales_df["week_number"] < planning_week)].copy()

    # Delegate directly to Phase 3A engine
    result = allocate_inventory(
        sales_history_df=hist_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=planning_week,
        warehouse_available=warehouse_available,
        capital_budget_limit=capital_budget_limit,
    )

    return result
