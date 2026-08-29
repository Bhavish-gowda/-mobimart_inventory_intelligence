"""
API Inventory Endpoint Tests.
"""

def test_inventory_list_status(client):
    r = client.get("/api/v1/inventory")
    assert r.status_code == 200

def test_inventory_response_structure(client):
    r = client.get("/api/v1/inventory")
    j = r.json()
    assert "records" in j
    assert "count" in j
    assert j["count"] > 0

def test_inventory_filter_by_store(client):
    r = client.get("/api/v1/inventory?store_id=STORE_01")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] == 60  # 60 products per store
    for rec in j["records"]:
        assert rec["store_id"] == "STORE_01"

def test_inventory_filter_by_product(client):
    r = client.get("/api/v1/inventory?product_id=PROD_001")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] == 25  # 25 stores
    for rec in j["records"]:
        assert rec["product_id"] == "PROD_001"

def test_inventory_filter_by_store_and_product(client):
    r = client.get("/api/v1/inventory?store_id=STORE_01&product_id=PROD_001")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] == 1

def test_inventory_summary_status(client):
    r = client.get("/api/v1/inventory/summary")
    assert r.status_code == 200

def test_inventory_summary_structure(client):
    r = client.get("/api/v1/inventory/summary")
    j = r.json()
    required_fields = [
        "total_units", "raw_cost_value", "operational_cost_value",
        "total_retail_value", "store_count", "sku_count",
        "capital_budget_limit", "capital_headroom", "capital_utilization_pct"
    ]
    for f in required_fields:
        assert f in j, f"Missing field: {f}"

def test_inventory_summary_capital_constraint(client):
    """Operational cost value must be <= ₹4 Crore capital budget limit."""
    r = client.get("/api/v1/inventory/summary")
    j = r.json()
    assert j["operational_cost_value"] <= j["capital_budget_limit"]

def test_inventory_summary_store_count_is_25(client):
    r = client.get("/api/v1/inventory/summary")
    assert r.json()["store_count"] == 25

def test_inventory_summary_sku_count_is_60(client):
    r = client.get("/api/v1/inventory/summary")
    assert r.json()["sku_count"] == 60

def test_inventory_summary_capital_utilization_is_pct(client):
    r = client.get("/api/v1/inventory/summary")
    pct = r.json()["capital_utilization_pct"]
    assert 0.0 <= pct <= 100.0

def test_inventory_summary_deterministic(client):
    r1 = client.get("/api/v1/inventory/summary")
    r2 = client.get("/api/v1/inventory/summary")
    assert r1.json()["operational_cost_value"] == r2.json()["operational_cost_value"]
