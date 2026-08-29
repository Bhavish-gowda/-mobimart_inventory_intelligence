"""
API Standardized Error Response Tests.
"""

def test_product_not_found_error_payload(client):
    r = client.get("/api/v1/products/PROD_NONEXISTENT")
    assert r.status_code == 404
    j = r.json()
    assert "error" in j
    err = j["error"]
    assert err["code"] == "PRODUCT_NOT_FOUND"
    assert "PROD_NONEXISTENT" in err["message"]
    assert "details" in err

def test_store_not_found_error_payload(client):
    r = client.get("/api/v1/stores/STORE_NONEXISTENT")
    assert r.status_code == 404
    j = r.json()
    assert "error" in j
    err = j["error"]
    assert err["code"] == "STORE_NOT_FOUND"
    assert "STORE_NONEXISTENT" in err["message"]

def test_validation_error_payload(client):
    r = client.post("/api/v1/forecast", json={
        "store_id": "STORE_01",
        "product_id": "PROD_001",
        "planning_week": -5
    })
    assert r.status_code == 422
    j = r.json()
    assert "error" in j
    err = j["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "details" in err
