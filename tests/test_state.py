from passive_drone_rf_observer.state import ObservationState


def test_observation_state_buffers_and_snapshot():
    state = ObservationState(max_events=2, max_alerts=2, max_wifi_observations=2, max_wifi_environment_events=2)

    state.append_rf_event({"id": 1}, is_drone_like=False)
    state.append_rf_event({"id": 2}, is_drone_like=True)
    state.append_alert({"level": "low", "message": "test", "timestamp": 1.0, "probability": 0.3, "source": "simulated_rf"})
    state.append_alert({"level": "medium", "message": "test2", "timestamp": 2.0, "probability": 0.6, "source": "simulated_rf"})

    assert len(state.get_events()) == 2
    assert state.total_events == 2
    assert state.drone_like_events == 1
    assert len(state.get_alerts()) == 2
    assert state.get_alerts()[0]["level"] == "medium"

    state.clear_rf_events()
    assert state.total_events == 0
    assert state.get_events() == []
    assert state.get_alerts()[0]["level"] == "medium"

    state.update_wifi_data([{"ssid": "A"}], [{"event_type": "new_network_seen"}], scan_ts=123.0)
    assert state.get_wifi_observations()[0]["ssid"] == "A"
    assert state.get_wifi_environment_events()[0]["event_type"] == "new_network_seen"
    assert state.last_wifi_scan_ts == 123.0

    state.clear_wifi_data()
    assert state.get_wifi_observations() == []
    assert state.get_wifi_environment_events() == []
    assert state.last_wifi_scan_ts is None
