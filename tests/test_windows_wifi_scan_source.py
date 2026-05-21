from unittest.mock import patch, MagicMock

from passive_drone_rf_observer.sources.windows_wifi_scan_source import WindowsWifiScanSource


SAMPLE_NETSH_OUTPUT = """
SSID 1 : HomeNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:11:22:33:44:55
         Signal             : 75%
         Radio type         : 802.11n
         Channel            : 6

SSID 2 : Guest
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 48%
         Radio type         : 802.11g
         Channel            : 11
"""


def test_windows_wifi_scan_parse(monkeypatch):
    fake_result = MagicMock()
    fake_result.returncode = 0
    fake_result.stdout = SAMPLE_NETSH_OUTPUT
    fake_result.stderr = ""

    monkeypatch.setattr("passive_drone_rf_observer.sources.windows_wifi_scan_source.platform.system", lambda: "Windows")
    monkeypatch.setattr("passive_drone_rf_observer.sources.windows_wifi_scan_source.subprocess.run", lambda *args, **kwargs: fake_result)

    source = WindowsWifiScanSource(salt="test-salt")
    observations = source.scan()

    assert len(observations) == 2
    assert observations[0].ssid == "HomeNetwork"
    assert observations[0].signal_percent == 75
    assert observations[0].channel == 6
    assert observations[0].radio_type == "802.11n"
    assert observations[0].authentication == "WPA2-Personal"
    assert observations[0].bssid_hash != "00:11:22:33:44:55"
    assert observations[1].ssid == "Guest"
    assert observations[1].signal_percent == 48
    assert observations[1].bssid_hash != "aa:bb:cc:dd:ee:ff"


def test_windows_wifi_scan_unsupported_platform(monkeypatch):
    monkeypatch.setattr("passive_drone_rf_observer.sources.windows_wifi_scan_source.platform.system", lambda: "Linux")
    source = WindowsWifiScanSource(salt="test-salt")
    observations = source.scan()
    assert observations == []
