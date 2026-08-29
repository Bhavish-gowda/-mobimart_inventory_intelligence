"""
Unit tests for Strategy A — Last-4-Week Proportional Baseline Allocator.
"""

import pandas as pd
import pytest

from backend.engine.simulation.baseline import allocate_baseline_inventory

@pytest.fixture
def sample_setup():
    stores = [
        {"id": "STORE_A", "name": "Store A", "city": "Bangalore"},
        {"id": "STORE_B", "name": "Store B", "city": "Bangalore"},
        {"id": "STORE_C", "name": "Store C", "city": "Mysore"},
    ]
    products = [
        {"id": "PROD_001", "model_name": "Nova 1", "segment": "Budget", "cost_price": 5000.0, "retail_price": 6500.0},
    ]
    inventory_records = [
        {"store_id": "STORE_A", "product_id": "PROD_001", "current_stock": 0, "in_transit_stock": 0},
        {"store_id": "STORE_B", "product_id": "PROD_001", "current_stock": 0, "in_transit_stock": 0},
        {"store_id": "STORE_C", "product_id": "PROD_001", "current_stock": 0, "in_transit_stock": 0},
    ]
    return stores, products, inventory_records

def test_proportional_allocation_correctness(sample_setup):
    stores, products, inventory_records = sample_setup
    
    # Store A = 10, Store B = 20, Store C = 30 over weeks 1..4 (Total = 60 sales)
    sales_data = []
    for wk in range(1, 5):
        sales_data.append({"week_number": wk, "store_id": "STORE_A", "product_id": "PROD_001", "units_sold": 2.5})
        sales_data.append({"week_number": wk, "store_id": "STORE_B", "product_id": "PROD_001", "units_sold": 5.0})
        sales_data.append({"week_number": wk, "store_id": "STORE_C", "product_id": "PROD_001", "units_sold": 7.5})
    
    sales_df = pd.DataFrame(sales_data)
    warehouse_stock = {"PROD_001": 12}

    alloc = allocate_baseline_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=5,
        warehouse_stock=warehouse_stock,
        high_risk_eol_product_ids=set(),
    )

    # 10/60 -> 2, 20/60 -> 4, 30/60 -> 6
    assert alloc.get(("STORE_A", "PROD_001")) == 2
    assert alloc.get(("STORE_B", "PROD_001")) == 4
    assert alloc.get(("STORE_C", "PROD_001")) == 6

def test_only_last_four_weeks_used(sample_setup):
    stores, products, inventory_records = sample_setup

    sales_data = []
    # Old weeks 1..5: Store A had 100 sales
    for wk in range(1, 6):
        sales_data.append({"week_number": wk, "store_id": "STORE_A", "product_id": "PROD_001", "units_sold": 20})
    # Recent weeks 6..9: Store B had 100 sales, Store A had 0 sales
    for wk in range(6, 10):
        sales_data.append({"week_number": wk, "store_id": "STORE_B", "product_id": "PROD_001", "units_sold": 25})

    sales_df = pd.DataFrame(sales_data)
    warehouse_stock = {"PROD_001": 10}

    alloc = allocate_baseline_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=10,
        warehouse_stock=warehouse_stock,
        high_risk_eol_product_ids=set(),
        lookback_weeks=4,
    )

    # Store A should get 0 because weeks 6..9 sales for A were 0
    assert alloc.get(("STORE_A", "PROD_001"), 0) == 0
    assert alloc.get(("STORE_B", "PROD_001")) == 10

def test_zero_historical_sales_handling(sample_setup):
    stores, products, inventory_records = sample_setup
    sales_df = pd.DataFrame(columns=["week_number", "store_id", "product_id", "units_sold"])
    warehouse_stock = {"PROD_001": 50}

    alloc = allocate_baseline_inventory(
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        planning_week=5,
        warehouse_stock=warehouse_stock,
        high_risk_eol_product_ids=set(),
    )
    assert len(alloc) == 0

def test_single_store_case(sample_setup):
    stores, products, inventory_records = sample_setup
    single_store = [stores[0]]
    single_inv = [inventory_records[0]]

    sales_data = [{"week_number": wk, "store_id": "STORE_A", "product_id": "PROD_001", "units_sold": 10} for wk in range(1, 5)]
    sales_df = pd.DataFrame(sales_data)
    warehouse_stock = {"PROD_001": 10}

    alloc = allocate_baseline_inventory(
        sales_history_df=sales_df,
        stores=single_store,
        products=products,
        inventory_records=single_inv,
        planning_week=5,
        warehouse_stock=warehouse_stock,
        high_risk_eol_product_ids=set(),
    )
    assert alloc.get(("STORE_A", "PROD_001")) == 10

def test_capital_constraint_respected(sample_setup):
    stores, products, inventory_records = sample_setup
    # High cost product ₹3,95,00,000 existing capital
    prod_high = [{"id": "PROD_001", "model_name": "Nova 1", "segment": "Flagship", "cost_price": 50000.0, "retail_price": 60000.0}]
    
    sales_data = [{"week_number": wk, "store_id": "STORE_A", "product_id": "PROD_001", "units_sold": 10} for wk in range(1, 5)]
    sales_df = pd.DataFrame(sales_data)
    
    # Stock 790 units * 50,000 = ₹3,95,00,000
    inv_near_cap = [{"store_id": "STORE_A", "product_id": "PROD_001", "current_stock": 790, "in_transit_stock": 0}]
    warehouse_stock = {"PROD_001": 100}

    alloc = allocate_baseline_inventory(
        sales_history_df=sales_df,
        stores=[stores[0]],
        products=prod_high,
        inventory_records=inv_near_cap,
        planning_week=5,
        warehouse_stock=warehouse_stock,
        high_risk_eol_product_ids=set(),
        capital_budget_limit=40000000.0,  # ₹4 Cr
    )

    # Remaining headroom is ₹5,00,000 -> Max 10 units of ₹50,000 can be allocated
    allocated_units = alloc.get(("STORE_A", "PROD_001"), 0)
    assert allocated_units <= 10
    assert allocated_units * 50000.0 + 39500000.0 <= 40000000.0
