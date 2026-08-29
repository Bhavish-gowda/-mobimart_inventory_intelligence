"""
API Endpoint Determinism & Idempotency Tests.
"""

def test_stores_determinism(client):
    r1 = client.get("/api/v1/stores")
    r2 = client.get("/api/v1/stores")
    assert r1.json() == r2.json()

def test_products_determinism(client):
    r1 = client.get("/api/v1/products")
    r2 = client.get("/api/v1/products")
    assert r1.json() == r2.json()

def test_forecast_determinism(client):
    req = {"store_id": "STORE_01", "product_id": "PROD_001", "planning_week": 24}
    r1 = client.post("/api/v1/forecast", json=req)
    r2 = client.post("/api/v1/forecast", json=req)
    assert r1.json() == r2.json()

def test_allocation_determinism(client):
    req = {"planning_week": 20, "capital_budget_limit": 40000000.0}
    r1 = client.post("/api/v1/allocation/run", json=req)
    r2 = client.post("/api/v1/allocation/run", json=req)
    assert r1.json() == r2.json()

def test_eol_risk_determinism(client):
    r1 = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    r2 = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    assert r1.json() == r2.json()

def test_simulation_determinism(client):
    req = {
        "strategy_name": "MOBIMART",
        "config": {"start_week": 1, "end_week": 2, "capital_budget_limit": 40000000.0}
    }
    r1 = client.post("/api/v1/simulation/run", json=req)
    r2 = client.post("/api/v1/simulation/run", json=req)
    j1 = r1.json()
    j2 = r2.json()
    assert j1["stockout_rate"] == j2["stockout_rate"]
    assert j1["total_revenue"] == j2["total_revenue"]
