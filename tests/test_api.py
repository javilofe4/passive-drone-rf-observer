import time
from fastapi.testclient import TestClient
from passive_drone_rf_observer.api.app import app, manager


client = TestClient(app)


def test_api_status_returns_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "running" in response.json()
    assert "config" in response.json()


def test_api_simulation_start_stop():
    manager.stop()
    response = client.post("/api/simulation/start")
    assert response.status_code == 200
    assert response.json()["running"] is True

    time.sleep(0.2)

    response = client.post("/api/simulation/stop")
    assert response.status_code == 200
    assert response.json()["running"] is False


def test_api_events_and_clear():
    manager.stop()
    client.post("/api/simulation/start")
    time.sleep(0.2)
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 0

    clear_response = client.post("/api/events/clear")
    assert clear_response.status_code == 200
    response_after_clear = client.get("/api/events")
    assert response_after_clear.status_code == 200
    assert response_after_clear.json() == []
    client.post("/api/simulation/stop")


def test_api_simulation_mode_change():
    response = client.post("/api/simulation/mode", json={"mode": "drone_activity"})
    assert response.status_code == 200
    assert response.json()["mode"] == "drone_activity"
    manager.set_mode("normal")
