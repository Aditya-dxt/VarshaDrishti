from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_historical_list():
    response = client.get("/api/historical")
    assert response.status_code == 200, "Should return HTTP 200"
    data = response.json()
    assert "events" in data, "Should return an events list"
    assert len(data["events"]) == 2, "Should return exactly two events"
    
    event_ids = [e["id"] for e in data["events"]]
    assert "event_2026-08-17" in event_ids
    assert "event_2026-08-18" in event_ids

def test_get_historical_detail_valid():
    response = client.get("/api/historical/event_2026-08-17")
    assert response.status_code == 200, "Should return HTTP 200 for valid event"
    data = response.json()
    assert data["event"]["id"] == "event_2026-08-17"
    assert data["event"]["latitude"] is None
    assert data["event"]["longitude"] is None
    assert "prediction" in data
    
    response2 = client.get("/api/historical/event_2026-08-18")
    assert response2.status_code == 200, "Should return HTTP 200 for valid event"
    data2 = response2.json()
    assert data2["event"]["id"] == "event_2026-08-18"
    assert data2["event"]["latitude"] is None
    assert data2["event"]["longitude"] is None
    assert "prediction" in data2

def test_get_historical_detail_invalid():
    response = client.get("/api/historical/invalid_event_123")
    assert response.status_code == 404, "Should return HTTP 404 for unknown event"
