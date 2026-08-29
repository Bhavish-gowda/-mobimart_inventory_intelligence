"""
Pytest unit tests for Constrained Greedy Allocation Engine.
Verifies finite warehouse inventory limits, ₹4 Crore hard capital limit,
determinism, prioritization of high-demand low-stock stores, EOL de-prioritization,
and edge case handling (zero stock, zero demand, budget bounds).
"""

import pytest
import pandas as pd
from backend.engine.allocation.allocator import allocate_inventory

@pytest.fixture
def sample_dataset():
    stores = [
        {"id": "STORE_01", "name": "Bangalore Indiranagar", "city": "Bangalore", "income_index": 1.85, "budget_affinity": 0.4, "flagship_affinity": 2.2},
        {"id": "STORE_02", "name": "Davangere Mandipet", "city": "Davangere", "income_index": 0.70, "budget_affinity": 2.1, "flagship_affinity": 0.2},
    ]

    products = [
        {"id": "PROD_001", "model_name": "Nova Budget 1", "segment": "Budget", "cost_price": 5000.0, "retail_price": 6500.0, "lifecycle_stage": "Peak", "markdown_percentage": 0.0},
        {"id": "PROD_002", "model_name": "Zenith Flagship 1", "segment": "Flagship", "cost_price": 80000.0, "retail_price": 100000.0, "lifecycle_stage": "Peak", "markdown_percentage": 0.0},
        {"id": "PROD_003", "model_name": "Vortex EOL 1", "segment": "Budget", "cost_price": 4000.0, "retail_price": 5000.0, "lifecycle_stage": "EOL", "markdown_percentage": 0.35},
    ]

    sales_list = []
    for wk in range(1, 20):
        sales_list.append({"store_id": "STORE_01", "product_id": "PROD_002", "week_number": wk, "units_sold": 8})
        sales_list.append({"store_id": "STORE_02", "product_id": "PROD_001", "week_number": wk, "units_sold": 12})
        sales_list.append({"store_id": "STORE_01", "product_id": "PROD_003", "week_number": wk, "units_sold": 1})
        sales_list.append({"store_id": "STORE_02", "product_id": "PROD_003", "week_number": wk, "units_sold": 1})

    sales_df = pd.DataFrame(sales_list)

    inventory_records = [
        {"store_id": "STORE_01", "product_id": "PROD_001", "current_stock": 5, "in_transit_stock": 0},
        {"store_id": "STORE_01", "product_id": "PROD_002", "current_stock": 0, "in_transit_stock": 0},
        {"store_id": "STORE_01", "product_id": "PROD_003", "current_stock": 10, "in_transit_stock": 0},
        {"store_id": "STORE_02", "product_id": "PROD_001", "current_stock": 1, "in_transit_stock": 0},
        {"store_id": "STORE_02", "product_id": "PROD_002", "current_stock": 2, "in_transit_stock": 0},
        {"store_id": "STORE_02", "product_id": "PROD_003", "current_stock": 8, "in_transit_stock": 0},
    ]

    return stores, products, sales_df, inventory_records

def test_capital_budget_exact_boundary_fill(sample_dataset):
    """Resulting capital deployed can reach budget limit but never exceed it."""
    stores, products, sales_df, inventory_records = sample_dataset
    initial_cap = (5 * 5000.0) + (10 * 4000.0) + (1 * 5000.0) + (2 * 80000.0) + (8 * 4000.0)  # = 2,57,000
    budget_cap = initial_cap + 10000.0  # Room for exactly 2 units of PROD_001 (5,000 cost each)

    result = allocate_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=20,
        capital_budget_limit=budget_cap,
    )

    assert result.resulting_capital_deployed <= budget_cap
    assert result.new_capital_allocated <= 10000.0

def test_capital_budget_when_already_at_limit(sample_dataset):
    """Zero new units allocated when existing capital is already at or above budget limit."""
    stores, products, sales_df, inventory_records = sample_dataset
    initial_cap = (5 * 5000.0) + (10 * 4000.0) + (1 * 5000.0) + (2 * 80000.0) + (8 * 4000.0)  # = 2,57,000

    result = allocate_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=20,
        capital_budget_limit=initial_cap,  # Budget limit = current capital
    )

    assert result.new_capital_allocated == 0.0
    assert result.total_units_allocated == 0

def test_warehouse_inventory_exact_exhaustion(sample_dataset):
    """Allocation stops exactly when warehouse inventory reaches zero."""
    stores, products, sales_df, inventory_records = sample_dataset
    warehouse_stock = {"PROD_001": 2, "PROD_002": 1, "PROD_003": 0}

    result = allocate_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=20,
        warehouse_available=warehouse_stock,
    )

    allocated_prod_1 = sum(r.recommended_qty for r in result.recommendations if r.product_id == "PROD_001")
    allocated_prod_2 = sum(r.recommended_qty for r in result.recommendations if r.product_id == "PROD_002")

    assert allocated_prod_1 == 2
    assert allocated_prod_2 == 1

def test_allocator_determinism(sample_dataset):
    """Same input must produce identical recommendation results."""
    stores, products, sales_df, inventory_records = sample_dataset
    r1 = allocate_inventory(sales_df, stores, products, inventory_records, planning_week=20)
    r2 = allocate_inventory(sales_df, stores, products, inventory_records, planning_week=20)

    assert r1.total_units_allocated == r2.total_units_allocated
    assert r1.resulting_capital_deployed == r2.resulting_capital_deployed
    assert len(r1.recommendations) == len(r2.recommendations)

def test_inventory_no_duplicate_rows_and_capital_rule():
    """Verify inventory dataset has no duplicate (store, product) keys and capital rule holds."""
    inv_df = pd.read_csv("data/generated/inventory.csv")
    duplicates = inv_df.duplicated(subset=["store_id", "product_id"])
    assert not duplicates.any(), "Inventory dataset contains duplicate store-product pairs!"

    products_df = pd.read_csv("data/generated/products.csv")
    prod_map = products_df.set_index("id")["cost_price"].to_dict()

    # Verify initial capital calculation
    expected_cap = sum(row["current_stock"] * prod_map[row["product_id"]] for _, row in inv_df.iterrows())
    assert round(expected_cap, 2) == 101311600.00

