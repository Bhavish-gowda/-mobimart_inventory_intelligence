"""
Automated Pytest test suite for MobiMart Synthetic Data Generator.
Verifies all 17 explicit requirements:
1. Exactly 25 stores are generated.
2. Exactly 60 products are generated.
3. 52 weeks are represented.
4. No negative prices.
5. Cost price < retail price.
6. No negative demand.
7. No negative sales.
8. Store IDs are unique.
9. Product IDs are unique.
10. Successor references are valid.
11. No product is its own successor.
12. Generator is deterministic with seed=42.
13. Bangalore stores have meaningfully different segment mix from tier-2/3 stores.
14. Festive weeks show higher demand.
15. Predecessor demand declines after successor launch.
16. Lifecycle stages are represented.
17. Rumoured and confirmed launches are distinguishable.
"""

import pytest
import pandas as pd
from backend.engine.generator.generator import generate_complete_dataset

@pytest.fixture(scope="module")
def dataset():
    """Generate dataset once for all unit tests."""
    return generate_complete_dataset(seed=42)

def test_1_store_count(dataset):
    """1. Exactly 25 stores are generated."""
    stores = dataset["stores"]
    assert len(stores) == 25, f"Expected 25 stores, found {len(stores)}"

def test_2_product_count(dataset):
    """2. Exactly 60 products are generated."""
    products = dataset["products"]
    assert len(products) == 60, f"Expected 60 products, found {len(products)}"

def test_3_52_weeks(dataset):
    """3. 52 weeks are represented."""
    sales = dataset["sales_history"]
    unique_weeks = sorted(sales["week_number"].unique().tolist())
    assert unique_weeks == list(range(1, 53)), "Sales history must represent weeks 1 through 52"

def test_4_no_negative_prices(dataset):
    """4. No negative prices."""
    products = dataset["products"]
    assert (products["cost_price"] > 0).all(), "Cost prices must be strictly positive"
    assert (products["retail_price"] > 0).all(), "Retail prices must be strictly positive"
    assert (products["margin"] > 0).all(), "Margins must be strictly positive"

def test_5_cost_less_than_retail(dataset):
    """5. Cost price < retail price."""
    products = dataset["products"]
    assert (products["cost_price"] < products["retail_price"]).all(), "Cost price must be strictly less than retail price for all SKUs"

def test_6_no_negative_demand(dataset):
    """6. No negative demand."""
    sales = dataset["sales_history"]
    assert (sales["demand_units"] >= 0).all(), "Demand units must be non-negative"

def test_7_no_negative_sales(dataset):
    """7. No negative sales."""
    sales = dataset["sales_history"]
    assert (sales["units_sold"] >= 0).all(), "Units sold must be non-negative"
    assert (sales["lost_sales_estimated"] >= 0).all(), "Lost sales must be non-negative"

def test_8_unique_store_ids(dataset):
    """8. Store IDs are unique."""
    stores = dataset["stores"]
    assert stores["id"].is_unique, "Store IDs must be globally unique"

def test_9_unique_product_ids(dataset):
    """9. Product IDs are unique."""
    products = dataset["products"]
    assert products["id"].is_unique, "Product IDs must be globally unique"

def test_10_valid_successor_references(dataset):
    """10. Successor references are valid."""
    products = dataset["products"]
    valid_ids = set(products["id"].unique())
    for succ_id in products["successor_product_id"].dropna():
        assert succ_id in valid_ids, f"Successor ID {succ_id} does not exist in products table"

def test_11_no_self_successor(dataset):
    """11. No product is its own successor."""
    products = dataset["products"]
    for _, row in products.dropna(subset=["successor_product_id"]).iterrows():
        assert row["id"] != row["successor_product_id"], f"Product {row['id']} cannot be its own successor"

def test_12_determinism(dataset):
    """12. Generator is deterministic with seed=42."""
    ds2 = generate_complete_dataset(seed=42)
    pd.testing.assert_frame_equal(dataset["stores"], ds2["stores"])
    pd.testing.assert_frame_equal(dataset["products"], ds2["products"])
    pd.testing.assert_frame_equal(dataset["sales_history"], ds2["sales_history"])

def test_13_city_segment_differences(dataset):
    """13. Bangalore stores have meaningfully different segment mix from tier-2/3 stores."""
    sales = dataset["sales_history"].merge(dataset["stores"], left_on="store_id", right_on="id")
    sales = sales.merge(dataset["products"], left_on="product_id", right_on="id")

    blr_flagship = sales[(sales["city"] == "Bangalore") & (sales["segment"] == "Flagship")]["units_sold"].sum()
    blr_total = sales[sales["city"] == "Bangalore"]["units_sold"].sum()
    blr_flagship_share = blr_flagship / max(1, blr_total)

    davangere_flagship = sales[(sales["city"] == "Davangere") & (sales["segment"] == "Flagship")]["units_sold"].sum()
    davangere_total = sales[sales["city"] == "Davangere"]["units_sold"].sum()
    davangere_flagship_share = davangere_flagship / max(1, davangere_total)

    assert blr_flagship_share > davangere_flagship_share, (
        f"Bangalore flagship sales share ({blr_flagship_share:.3f}) must exceed Davangere flagship sales share ({davangere_flagship_share:.3f})"
    )

def test_14_festive_demand_surge(dataset):
    """14. Festive weeks show higher demand."""
    sales = dataset["sales_history"]
    normal_w20_demand = sales[sales["week_number"] == 20]["demand_units"].sum()
    diwali_w42_demand = sales[sales["week_number"] == 42]["demand_units"].sum()

    assert diwali_w42_demand > 1.5 * normal_w20_demand, (
        f"Diwali demand ({diwali_w42_demand}) must show significant surge over normal week 20 demand ({normal_w20_demand})"
    )

def test_15_successor_cannibalization(dataset):
    """15. Predecessor demand declines after successor launch."""
    sales = dataset["sales_history"]
    # Apex Note 11 (PROD_019) has successor Apex Note 12 launching week 18
    pre_launch_avg = sales[(sales["product_id"] == "PROD_019") & (sales["week_number"] < 18)]["demand_units"].mean()
    post_launch_avg = sales[(sales["product_id"] == "PROD_019") & (sales["week_number"] >= 25)]["demand_units"].mean()

    assert post_launch_avg < pre_launch_avg, (
        f"Predecessor demand post-successor launch ({post_launch_avg:.2f}) must be lower than pre-launch demand ({pre_launch_avg:.2f})"
    )

def test_16_lifecycle_stages_represented(dataset):
    """16. Lifecycle stages are represented."""
    products = dataset["products"]
    stages = set(products["lifecycle_stage"].unique())
    expected_stages = {"Launch", "Growth", "Peak", "Decline", "EOL"}
    assert stages == expected_stages, f"Expected all lifecycle stages {expected_stages}, found {stages}"

def test_17_rumoured_vs_confirmed(dataset):
    """17. Rumoured and confirmed launches are distinguishable."""
    products = dataset["products"]
    confirmed = products[products["is_rumoured"] == False]
    rumoured = products[products["is_rumoured"] == True]

    assert len(confirmed) > 0, "Must have confirmed product launches"
    assert len(rumoured) > 0, "Must have rumoured product launches"
    assert (confirmed["launch_confidence"] == 1.0).all(), "Confirmed launches must have launch_confidence = 1.0"
    assert ((rumoured["launch_confidence"] >= 0.3) & (rumoured["launch_confidence"] <= 0.7)).all(), (
        "Rumoured launches must have launch_confidence between 0.3 and 0.7"
    )
