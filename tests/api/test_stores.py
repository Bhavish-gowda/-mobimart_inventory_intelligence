"""
API Store Endpoint Tests.
"""

def test_stores_list_status(client):
    r = client.get("/api/v1/stores")
    assert r.status_code == 200

def test_stores_count_is_25(client):
    r = client.get("/api/v1/stores")
    j = r.json()
    assert j["count"] == 25
    assert len(j["stores"]) == 25

def test_stores_response_schema(client):
    r = client.get("/api/v1/stores")
    store = r.json()["stores"][0]
    assert "id" in store
    assert "name" in store
    assert "city" in store
    assert "location_type" in store

def test_stores_filter_by_city(client):
    r = client.get("/api/v1/stores?city=Bangalore")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] == 8
    for s in j["stores"]:
        assert s["city"] == "Bangalore"

def test_stores_filter_by_city_case_insensitive(client):
    r1 = client.get("/api/v1/stores?city=bangalore")
    r2 = client.get("/api/v1/stores?city=Bangalore")
    assert r1.json()["count"] == r2.json()["count"]

def test_stores_filter_by_location_type(client):
    r = client.get("/api/v1/stores?location_type=High%20Street")
    j = r.json()
    assert r.status_code == 200
    assert j["count"] >= 1
    for s in j["stores"]:
        assert s["location_type"].lower() == "high street"

def test_stores_empty_filter_returns_all(client):
    r = client.get("/api/v1/stores")
    assert r.json()["count"] == 25

def test_stores_deterministic(client):
    r1 = client.get("/api/v1/stores")
    r2 = client.get("/api/v1/stores")
    assert r1.json()["count"] == r2.json()["count"]
    assert r1.json()["stores"][0]["id"] == r2.json()["stores"][0]["id"]
