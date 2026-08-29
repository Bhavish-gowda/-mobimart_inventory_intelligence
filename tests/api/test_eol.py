"""
API EOL Risk & Portfolio Transfer Endpoint Tests.
"""

def test_eol_risk_status(client):
    r = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    assert r.status_code == 200

def test_eol_risk_response_schema(client):
    r = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    j = r.json()
    assert "current_week" in j
    assert "assessments" in j
    assert "portfolio_resolution" in j
    res = j["portfolio_resolution"]
    assert "approved_routes" in res
    assert "rejected_routes" in res
    assert "candidate_transfer_opportunity" in res
    assert "approved_transfer_opportunity" in res
    assert "source_capacity_ledger" in res
    assert "destination_capacity_ledger" in res

def test_eol_assess_position_status(client):
    r = client.post("/api/v1/eol/assess", json={
        "store_id": "STORE_01",
        "product_id": "PROD_058",
        "current_week": 24
    })
    assert r.status_code == 200

def test_eol_assess_invalid_store(client):
    r = client.post("/api/v1/eol/assess", json={
        "store_id": "INVALID_STORE",
        "product_id": "PROD_058",
        "current_week": 24
    })
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "STORE_NOT_FOUND"

def test_eol_deterministic(client):
    r1 = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    r2 = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    assert r1.json()["assessments_count"] == r2.json()["assessments_count"]

def test_eol_portfolio_capacity_enforcement(client):
    """Verify that portfolio resolution ledgers respect capacity limits and candidate vs approved opportunity."""
    r = client.get("/api/v1/eol/risk?current_week=24&min_risk_level=MEDIUM")
    assert r.status_code == 200
    res = r.json()["portfolio_resolution"]
    
    # Approved transfer opportunity <= candidate transfer opportunity
    assert res["approved_transfer_opportunity"] <= res["candidate_transfer_opportunity"]
    
    # Verify each approved route respects source excess and destination shortfall
    for route in res["approved_routes"]:
        assert route["approved_units"] <= route["requested_units"]
        assert route["approved_units"] <= route["source_excess_units"]
        assert route["approved_units"] <= route["destination_shortfall_units"]
        assert route["status"] == "APPROVED"
