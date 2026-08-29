"""
API Product Endpoint Tests.
"""

def test_products_list_status(client):
    r = client.get("/api/v1/products")
    assert r.status_code == 200

def test_products_count_is_60(client):
    r = client.get("/api/v1/products")
    j = r.json()
    assert j["count"] == 60
    assert len(j["products"]) == 60

def test_products_response_schema(client):
    r = client.get("/api/v1/products")
    p = r.json()["products"][0]
    assert "id" in p
    assert "model_name" in p
    assert "segment" in p
    assert "cost_price" in p
    assert "retail_price" in p
    assert "lifecycle_stage" in p

def test_products_filter_by_segment(client):
    r = client.get("/api/v1/products?segment=Budget")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] >= 1
    for p in j["products"]:
        assert p["segment"] == "Budget"

def test_products_filter_by_lifecycle_stage(client):
    r = client.get("/api/v1/products?lifecycle_stage=EOL")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] >= 1
    for p in j["products"]:
        assert p["lifecycle_stage"] == "EOL"

def test_products_detail_status(client):
    r = client.get("/api/v1/products/PROD_001")
    assert r.status_code == 200

def test_products_detail_correct_id(client):
    r = client.get("/api/v1/products/PROD_001")
    assert r.json()["id"] == "PROD_001"

def test_products_detail_flagship(client):
    r = client.get("/api/v1/products/PROD_054")
    j = r.json()
    assert j["segment"] == "Flagship"

def test_products_detail_404(client):
    r = client.get("/api/v1/products/PROD_DOES_NOT_EXIST")
    assert r.status_code == 404

def test_products_detail_404_error_structure(client):
    r = client.get("/api/v1/products/PROD_DOES_NOT_EXIST")
    err = r.json()["error"]
    assert err["code"] == "PRODUCT_NOT_FOUND"
    assert "PROD_DOES_NOT_EXIST" in err["message"]

def test_products_nan_fields_are_null_not_nan(client):
    """Products with no successor should have null (not NaN) in API response."""
    r = client.get("/api/v1/products/PROD_001")
    j = r.json()
    # PROD_001 has no successor_product_id — must be None/null, never NaN
    assert j["successor_product_id"] is None

def test_products_deterministic(client):
    r1 = client.get("/api/v1/products")
    r2 = client.get("/api/v1/products")
    assert r1.json()["count"] == r2.json()["count"]
