"""
API Health Endpoint Tests.
"""

def test_health_status_ok(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200

def test_health_response_structure(client):
    r = client.get("/api/v1/health")
    j = r.json()
    assert j["status"] == "ok"
    assert j["service"] == "MobiMart Inventory Intelligence API"
    assert j["version"] == "1.0.0"

def test_health_is_deterministic(client):
    r1 = client.get("/api/v1/health")
    r2 = client.get("/api/v1/health")
    assert r1.json() == r2.json()
