"""
API Input Validation Bounds & Error Rejection Tests.
"""

def test_forecast_invalid_week_low(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 0
    })
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"

def test_forecast_invalid_week_high(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": 53
    })
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"

def test_allocation_invalid_week(client):
    r = client.post("/api/v1/allocation/run", json={
        "planning_week": 999,
        "capital_budget_limit": 40000000.0
    })
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"

def test_simulation_invalid_strategy(client):
    r = client.post("/api/v1/simulation/run", json={
        "strategy_name": "UNSUPPORTED_STRATEGY"
    })
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_REQUEST"

def test_inventory_pagination_out_of_bounds(client):
    r = client.get("/api/v1/inventory?page=-1")
    assert r.status_code == 422

def test_inventory_pagination_valid(client):
    r = client.get("/api/v1/inventory?page=1&page_size=10")
    assert r.status_code == 200
    j = r.json()
    assert len(j["records"]) == 10
    assert j["count"] == 1500
    assert j["page"] == 1
    assert j["page_size"] == 10
