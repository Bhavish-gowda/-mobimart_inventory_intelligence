"""
API Allocation Endpoint Tests.
"""

def test_allocation_run_status(client):
    r = client.post("/api/v1/allocation/run", json={
        "planning_week": 20,
        "capital_budget_limit": 40000000.0
    })
    assert r.status_code == 200

def test_allocation_run_response_schema(client):
    r = client.post("/api/v1/allocation/run", json={
        "planning_week": 20,
        "capital_budget_limit": 40000000.0
    })
    j = r.json()
    assert "run_id" in j
    assert "planning_week" in j
    assert "resulting_capital_deployed" in j
    assert "recommendations" in j
    assert isinstance(j["recommendations"], list)

def test_allocation_capital_constraint(client):
    r = client.post("/api/v1/allocation/run", json={
        "planning_week": 20,
        "capital_budget_limit": 105000000.0
    })
    j = r.json()
    assert j["resulting_capital_deployed"] <= 105000000.0

def test_allocation_deterministic(client):
    req = {
        "planning_week": 20,
        "capital_budget_limit": 40000000.0
    }
    r1 = client.post("/api/v1/allocation/run", json=req)
    r2 = client.post("/api/v1/allocation/run", json=req)
    assert r1.json()["run_id"] == r2.json()["run_id"]
    assert r1.json()["resulting_capital_deployed"] == r2.json()["resulting_capital_deployed"]

def test_allocation_warehouse_stock_override_respected(client):
    """Verify that custom warehouse stock limits override allocation capacities."""
    r = client.post("/api/v1/allocation/run", json={
        "planning_week": 20,
        "capital_budget_limit": 40000000.0,
        "warehouse_available": {"PROD_001": 0}  # Force zero warehouse stock for PROD_001
    })
    assert r.status_code == 200
    j = r.json()
    prod1_recs = [rec for rec in j["recommendations"] if rec["product_id"] == "PROD_001"]
    total_prod1_allocated = sum(rec["recommended_qty"] for rec in prod1_recs)
    assert total_prod1_allocated == 0, f"Expected 0 units allocated for PROD_001 when warehouse stock is 0, got {total_prod1_allocated}"
