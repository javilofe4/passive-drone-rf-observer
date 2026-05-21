from passive_drone_rf_observer.models import RFEvent
from passive_drone_rf_observer.agents.detector_agent import classify_event


def test_detector_classifies_noise():
    ev = RFEvent(timestamp=0, frequency_hz=100e6, bandwidth_hz=1e3, rssi_dbm=-100.0, duration_ms=10, source="test")
    cr = classify_event(ev)
    assert cr.label == "noise"


def test_detector_suggests_drone_like():
    ev = RFEvent(timestamp=0, frequency_hz=2.4e9, bandwidth_hz=2e6, rssi_dbm=-30.0, duration_ms=20, source="test")
    cr = classify_event(ev)
    assert cr.label in ("drone_like", "wifi_like", "unknown")
    assert 0.0 <= cr.score <= 1.0
