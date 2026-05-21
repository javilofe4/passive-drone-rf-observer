from passive_drone_rf_observer.hardware import (
    get_radio_hardware_profile,
    RadioHardwareProfile,
)
from passive_drone_rf_observer.config import load_config


def test_default_hardware_profile_is_simulated():
    profile = get_radio_hardware_profile("simulated")
    assert isinstance(profile, RadioHardwareProfile)
    assert profile.name == "simulated"
    assert profile.supports_rx_only is True


def test_config_defaults_rx_only_false_enable_sdr_false():
    cfg = load_config()
    assert cfg.rx_only is True
    assert cfg.enable_sdr is False
    assert cfg.enable_remote_id is False
    assert cfg.enable_wifi_monitor is False
    assert cfg.enable_hackrf is False
