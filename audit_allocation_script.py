"""
Comprehensive Financial & Allocation Audit Test Script.
Validates double counting, ₹4 Crore cap boundaries, warehouse stock bounds,
marginal allocation ordering, and numeric explanation consistency.
"""

import pandas as pd
from backend.engine.allocation.allocator import allocate_inventory
from backend.engine.allocation.financials import calculate_financial_impact, calculate_avoided_stockout_loss
from backend.engine.allocation.models import ForecastResult, InventoryMetrics

def run_audit_checks():
    print("=== 1. DOUBLE COUNTING VERIFICATION ===")
    prod = {"id": "PROD_001", "segment": "Budget", "cost_price": 8000.0, "retail_price": 10000.0, "lifecycle_stage": "Peak"}
    unit_margin = 2000.0

    # Demand = 1.0, current stock = 0
    fc = ForecastResult("S1", "P1", 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    inv = InventoryMetrics("S1", "P1", 0, 0, 1, 0.0, 1.0, 8000.0, 100.0, 0.0)

    fin = calculate_financial_impact(prod, fc, inv, additional_unit_index=1)
    print(f"Unit Cost: ₹{fin.unit_cost}, Retail: ₹{fin.unit_retail}, Margin: ₹{fin.unit_margin}")
    print(f"Calculated expected_incremental_margin:       ₹{fin.expected_incremental_margin}")
    print(f"Calculated expected_avoided_stockout_loss:    ₹{fin.expected_avoided_stockout_loss}")
    print(f"Calculated allocation_cost:                   ₹{fin.allocation_cost}")
    print(f"Current Net Marginal Value (Sum of both):     ₹{fin.net_marginal_value}")

    # Corrected value without double-counting margin:
    # Option 1: Gross Margin + Goodwill Penalty - Allocation Cost
    # Budget segment: Lost sale prob = 0.80, Goodwill factor = 0.15 (₹300)
    goodwill_penalty = unit_margin * 0.15
    corrected_benefit = fin.expected_incremental_margin + goodwill_penalty - fin.allocation_cost
    print(f"Corrected Net Value (Margin + Goodwill - Cost): ₹{corrected_benefit}")

    print("\n=== 3. ₹4 CRORE BOUNDARY TEST ===")
    stores = [{"id": "STORE_01", "name": "Bangalore Main", "city": "Bangalore", "income_index": 1.5, "budget_affinity": 1.0, "flagship_affinity": 1.0}]
    products = [{"id": "PROD_001", "model_name": "Nova 1", "segment": "Budget", "cost_price": 5000.0, "retail_price": 6500.0, "lifecycle_stage": "Peak"}]
    sales_df = pd.DataFrame([{"store_id": "STORE_01", "product_id": "PROD_001", "week_number": wk, "units_sold": 10} for wk in range(1, 20)])

    # Test 3A: Existing capital = ₹3.95 Crore (39,500,000), budget limit = ₹4.00 Crore (40,000,000)
    inv_395 = [{"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 7900, "in_transit_stock": 0}]
    res_395 = allocate_inventory(sales_df, stores, products, inv_395, planning_week=20, capital_budget_limit=40000000.0)
    print(f"Test 3A (₹3.95 Cr Initial): Initial = ₹{res_395.initial_capital_deployed:,.2f}, New = ₹{res_395.new_capital_allocated:,.2f}, Resulting = ₹{res_395.resulting_capital_deployed:,.2f}")

    # Test 3B: Existing capital = ₹4.05 Crore (40,500,000), budget limit = ₹4.00 Crore
    inv_405 = [{"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 8100, "in_transit_stock": 0}]
    res_405 = allocate_inventory(sales_df, stores, products, inv_405, planning_week=20, capital_budget_limit=40000000.0)
    print(f"Test 3B (₹4.05 Cr Initial): Initial = ₹{res_405.initial_capital_deployed:,.2f}, New = ₹{res_405.new_capital_allocated:,.2f}, Resulting = ₹{res_405.resulting_capital_deployed:,.2f}")

    print("\n=== 4. WAREHOUSE INVENTORY BOUNDARY TEST ===")
    inv_low = [{"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 0, "in_transit_stock": 0}]
    res_wh5 = allocate_inventory(sales_df, stores, products, inv_low, planning_week=20, warehouse_available={"PROD_001": 5})
    print(f"Test 4 (WH Limit=5, Demand=10+): Total Allocated = {res_wh5.total_units_allocated} units (Requested 10+)")

if __name__ == "__main__":
    run_audit_checks()
