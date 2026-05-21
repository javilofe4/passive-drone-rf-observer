from passive_drone_rf_observer.sources.simulated_rf_source import SimulatedRFSource


def test_simulated_source_yields_event():
    src = SimulatedRFSource()
    it = src.iter_events()
    ev = next(it)
    assert hasattr(ev, "timestamp")
    assert hasattr(ev, "frequency_hz")
    assert hasattr(ev, "rssi_dbm")
