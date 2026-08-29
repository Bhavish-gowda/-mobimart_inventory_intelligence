"""
API Schema Contract Validation Tests.
"""

def test_health_contract(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert "service" in j
    assert "version" in j

def test_readiness_contract(client):
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ready"
    assert j["data_loaded"] is True
    assert j["stores_count"] == 25
    assert j["products_count"] == 60

def test_stores_schema_contract(client):
    r = client.get("/api/v1/stores")
    assert r.status_code == 200
    j = r.json()
    assert "stores" in j
    assert "count" in j
    first = j["stores"][0]
    assert isinstance(first["id"], str)
    assert isinstance(first["name"], str)
    assert isinstance(first["city"], str)
    assert isinstance(first["location_type"], str)

def test_products_schema_contract(client):
    r = client.get("/api/v1/products")
    assert r.status_code == 200
    j = r.json()
    assert "products" in j
    assert "count" in j
    first = j["products"][0]
    assert isinstance(first["id"], str)
    assert isinstance(first["cost_price"], (int, float))
    assert isinstance(first["retail_price"], (int, float))
    assert isinstance(first["segment"], str)
    assert isinstance(first["lifecycle_stage"], str)

def test_inventory_summary_schema_contract(client):
    r = client.get("/api/v1/inventory/summary")
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j["total_units"], int)
    assert isinstance(j["raw_cost_value"], (int, float))
    assert isinstance(j["operational_cost_value"], (int, float))
    assert isinstance(j["capital_budget_limit"], (int, float))
    assert isinstance(j["capital_headroom"], (int, float))
    assert j["capital_budget_limit"] == 40000000.0
