import time

from passive_drone_rf_observer.agents.alert_agent import evaluate_alert, evaluate_wifi_alert
from passive_drone_rf_observer.models import WifiEnvironmentEvent


def make_env_event(event_type: str, score: float = 0.5, source: str = "windows_wifi_scan") -> WifiEnvironmentEvent:
    return WifiEnvironmentEvent(
        timestamp=time.time(),
        event_type=event_type,
        score=score,
        explanation="Test event",
        source=source,
    )


def test_evaluate_alert_has_simulated_source_by_default():
    alert = evaluate_alert(0.45)
    assert alert.level == "low"
    assert alert.source == "simulated_rf"
    assert "unusual RF activity" in alert.message


def test_evaluate_wifi_alert_returns_none_for_unknown_only():
    alert = evaluate_wifi_alert([make_env_event("unknown")])
    assert alert is None


def test_evaluate_wifi_alert_returns_low_for_single_interest():
    alert = evaluate_wifi_alert([make_env_event("new_network_seen")])
    assert alert is not None
    assert alert.level == "low"
    assert alert.source == "windows_wifi_scan"
    assert "Wireless activity of interest" in alert.message


def test_evaluate_wifi_alert_returns_medium_for_crowded_channel():
    alert = evaluate_wifi_alert([make_env_event("crowded_channel")])
    assert alert is not None
    assert alert.level == "medium"
    assert alert.source == "windows_wifi_scan"
    assert "Repeated strong local wireless activity" in alert.message
