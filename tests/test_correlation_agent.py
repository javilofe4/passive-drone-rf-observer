from passive_drone_rf_observer.agents.correlation_agent import Correlator
from passive_drone_rf_observer.models import RFEvent
import time


def make_event(ts_offset, score=0.6):
    return RFEvent(timestamp=time.time() + ts_offset, frequency_hz=2.4e9, bandwidth_hz=1e6, rssi_dbm=-40, duration_ms=10, source="test")


def test_correlation_aggregates():
    c = Correlator(window_s=2.0, min_events=2)
    e1 = make_event(0)
    r1 = c.add_event(e1, 0.6)
    e2 = make_event(0.5)
    r2 = c.add_event(e2, 0.7)
    assert r2.contributing_events >= 1
    assert 0.0 <= r2.probability <= 1.0
