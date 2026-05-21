import time

from passive_drone_rf_observer.agents.wifi_environment_agent import analyze_wifi_environment
from passive_drone_rf_observer.models import WifiObservation


def make_observation(bssid_hash: str, signal_percent: int, channel: int, ssid: str = "TestNet") -> WifiObservation:
    return WifiObservation(
        timestamp=time.time(),
        ssid=ssid,
        bssid_hash=bssid_hash,
        signal_percent=signal_percent,
        channel=channel,
        radio_type="802.11n",
        authentication="WPA2",
        source="windows_wifi_scan",
    )


def test_analyze_wifi_environment_new_and_strong_signal():
    observations = [
        make_observation("hash1", 60, 1, ssid="HomeWiFi"),
        make_observation("hash2", 80, 6, ssid="OfficeWiFi"),
    ]
    events, hashes, signals = analyze_wifi_environment(observations, known_hashes=set(), last_signals={})

    assert any(event.event_type == "new_network_seen" for event in events)
    assert any(event.event_type == "strong_signal_seen" for event in events)
    assert "hash1" in hashes and "hash2" in hashes
    assert signals["hash1"] == 60
    assert signals["hash2"] == 80


def test_analyze_wifi_environment_signal_change():
    first = make_observation("hash1", 40, 1)
    second = make_observation("hash1", 80, 1)
    events, hashes, signals = analyze_wifi_environment([first, second], known_hashes={"hash1"}, last_signals={"hash1": 40})

    assert any(event.event_type == "signal_changed" for event in events)
    assert any(event.event_type == "strong_signal_seen" for event in events)
    assert signals["hash1"] == 80


def test_analyze_wifi_environment_crowded_channel():
    observations = [make_observation(f"hash{i}", 50, 11) for i in range(5)]
    events, hashes, signals = analyze_wifi_environment(observations, known_hashes=set(), last_signals={})

    assert any(event.event_type == "crowded_channel" for event in events)
    assert len(hashes) == 5
    assert len(signals) == 5


def test_analyze_wifi_environment_empty_returns_unknown():
    events, hashes, signals = analyze_wifi_environment([], known_hashes=set(), last_signals={})

    assert len(events) == 1
    assert events[0].event_type == "unknown"
    assert hashes == set()
    assert signals == {}
