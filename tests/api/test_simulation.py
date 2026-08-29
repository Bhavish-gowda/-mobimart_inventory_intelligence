"""
API Simulation & Benchmark Endpoint Tests.
"""

def test_simulation_run_baseline(client):
    r = client.post("/api/v1/simulation/run", json={
        "strategy_name": "BASELINE",
        "config": {
            "start_week": 1,
            "end_week": 2,
            "capital_budget_limit": 40000000.0
        }
    })
    assert r.status_code == 200
    j = r.json()
    assert j["strategy_name"] == "BASELINE"
    assert "stockout_rate" in j
    assert "total_revenue" in j

def test_simulation_run_mobimart(client):
    r = client.post("/api/v1/simulation/run", json={
        "strategy_name": "MOBIMART",
        "config": {
            "start_week": 1,
            "end_week": 2,
            "capital_budget_limit": 40000000.0
        }
    })
    assert r.status_code == 200
    j = r.json()
    assert j["strategy_name"] == "MOBIMART"

def test_simulation_invalid_strategy(client):
    r = client.post("/api/v1/simulation/run", json={
        "strategy_name": "INVALID_STRATEGY"
    })
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_REQUEST"

def test_simulation_benchmark_post_endpoint(client):
    """Verify POST /api/v1/simulation/benchmark executes comparison."""
    r = client.post("/api/v1/simulation/benchmark?start_week=1&end_week=2")
    assert r.status_code == 200
    j = r.json()
    assert "baseline" in j
    assert "mobimart" in j
    assert "metrics" in j
    assert "summary_text" in j

def test_simulation_request_isolation(client):
    """Verify simulation runs maintain state isolation and do not mutate starting datasets."""
    req = {
        "strategy_name": "MOBIMART",
        "config": {"start_week": 1, "end_week": 2}
    }
    r1 = client.post("/api/v1/simulation/run", json=req)
    r2 = client.post("/api/v1/simulation/run", json=req)
    assert r1.json()["total_revenue"] == r2.json()["total_revenue"]
    assert r1.json()["starting_snapshot"] == r2.json()["starting_snapshot"]
