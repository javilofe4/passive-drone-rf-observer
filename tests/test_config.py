from passive_drone_rf_observer.config import load_config


def test_load_config_default_values():
    cfg = load_config({})
    assert cfg.rx_only is True
    assert cfg.enable_sdr is False
    assert cfg.enable_remote_id is False
    assert cfg.enable_wifi_monitor is False
    assert cfg.enable_hackrf is False
    assert cfg.enable_windows_wifi_scan is False
    assert cfg.hardware_profile == "simulated"
    assert cfg.log_db_path.name == "pdrfo_logs.db"


def test_load_config_environment_overrides():
    env = {
        "RX_ONLY": "false",
        "ENABLE_SDR": "true",
        "ENABLE_WINDOWS_WIFI_SCAN": "true",
        "PDRFO_HARDWARE_PROFILE": "rtl_sdr_v4",
        "PDRFO_LOG_DB_PATH": "./logs/test.db",
    }
    cfg = load_config(env)
    assert cfg.rx_only is False
    assert cfg.enable_sdr is True
    assert cfg.enable_windows_wifi_scan is True
    assert cfg.hardware_profile == "rtl_sdr_v4"
    assert cfg.log_db_path.name == "test.db"
