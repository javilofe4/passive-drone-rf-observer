import time
from fastapi.testclient import TestClient
from passive_drone_rf_observer.api.app import create_app
from passive_drone_rf_observer.config import Config


def make_test_client() -> TestClient:
    config = Config(
        simulation_duration_s=1,
        event_interval_s=0.01,
        correlation_window_s=1.0,
        min_events_for_alert=2,
        log_db_path="test_logs.db",
        rx_only=True,
        enable_sdr=False,
        enable_remote_id=False,
        enable_wifi_monitor=False,
        enable_hackrf=False,
        enable_windows_wifi_scan=False,
        wifi_scan_interval_s=5.0,
        wifi_bssid_salt="test-salt",
        hardware_profile="simulated",
    )
    app = create_app(config)
    return TestClient(app)


def test_api_status_returns_status():
    client = make_test_client()
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "running" in response.json()
    assert "config" in response.json()


def test_api_simulation_start_stop():
    client = make_test_client()
    response = client.post("/api/simulation/start")
    assert response.status_code == 200
    assert response.json()["running"] is True

    time.sleep(0.05)

    response = client.post("/api/simulation/stop")
    assert response.status_code == 200
    assert response.json()["running"] is False


def test_api_events_and_clear():
    client = make_test_client()
    client.post("/api/simulation/start")
    time.sleep(0.05)
    response = client.get("/api/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    clear_response = client.post("/api/events/clear")
    assert clear_response.status_code == 200
    response_after_clear = client.get("/api/events")
    assert response_after_clear.status_code == 200
    assert response_after_clear.json() == []
    client.post("/api/simulation/stop")


def test_api_simulation_mode_change():
    client = make_test_client()
    response = client.post("/api/simulation/mode", json={"mode": "drone_activity"})
    assert response.status_code == 200
    assert response.json()["mode"] == "drone_activity"


def test_api_wifi_endpoints():
    client = make_test_client()
    response = client.get("/api/wifi/observations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    scan_response = client.post("/api/wifi/scan")
    assert scan_response.status_code == 200
    assert isinstance(scan_response.json(), list)

    clear_response = client.post("/api/wifi/clear")
    assert clear_response.status_code == 200
    assert "running" in clear_response.json()
    response_after_clear = client.get("/api/wifi/observations")
    assert response_after_clear.status_code == 200
    assert response_after_clear.json() == []


def test_api_wifi_environment_events():
    client = make_test_client()
    response = client.get("/api/wifi/environment-events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
