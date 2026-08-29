"""
API Forecast Endpoint Tests.
"""

def test_forecast_status(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 24
    })
    assert r.status_code == 200

def test_forecast_response_schema(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 24
    })
    j = r.json()
    assert "store_id" in j
    assert "product_id" in j
    assert "forecast_weekly_demand" in j
    assert "confidence" in j

def test_forecast_invalid_store(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_DOES_NOT_EXIST",
        "product_id": "PROD_001",
        "planning_week": 24
    })
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "STORE_NOT_FOUND"

def test_forecast_invalid_product(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_DOES_NOT_EXIST",
        "planning_week": 24
    })
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

def test_forecast_deterministic(client):
    req = {
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 24
    }
    r1 = client.post("/api/v1/forecast", json=req)
    r2 = client.post("/api/v1/forecast", json=req)
    assert r1.json()["forecast_weekly_demand"] == r2.json()["forecast_weekly_demand"]

def test_forecast_leakage_protection_via_api(client):
    """Verify API demand forecast for week W is unaffected by future sales in week W+5."""
    from backend.api.data_loader import load_sales_history_df
    sales_df = load_sales_history_df()
    
    # Baseline forecast at week 20
    r1 = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 20
    })
    val1 = r1.json()["forecast_weekly_demand"]

    # Perturb future data (week 25 > week 20) in place
    future_mask = (sales_df["store_id"] == "STORE_01") & (sales_df["product_id"] == "PROD_001") & (sales_df["week_number"] == 25)
    original_units = sales_df.loc[future_mask, "units_sold"].values[0] if not sales_df[future_mask].empty else 0
    
    try:
        if not sales_df[future_mask].empty:
            sales_df.loc[future_mask, "units_sold"] = original_units + 1000
        
        # Forecast at week 20 must remain identical
        r2 = client.post("/api/v1/forecast", json={
            "store_id": "STORE_01",
            "product_id": "PROD_001",
            "planning_week": 20
        })
        val2 = r2.json()["forecast_weekly_demand"]
        assert val1 == val2, "Forecast for week 20 changed when future data (week 25) was perturbed!"
    finally:
        if not sales_df[future_mask].empty:
            sales_df.loc[future_mask, "units_sold"] = original_units
