from dataclasses import dataclass
import os


def _bool_env(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).strip().lower() in ("1", "true", "yes")


@dataclass
class Config:
    simulation_duration_s: int = int(os.getenv("PDRFO_SIM_DURATION", "6"))
    event_interval_s: float = float(os.getenv("PDRFO_EVENT_INTERVAL", "0.25"))
    correlation_window_s: float = float(os.getenv("PDRFO_CORRELATION_WINDOW", "2.0"))
    min_events_for_alert: int = int(os.getenv("PDRFO_MIN_EVENTS", "2"))
    log_db_path: str = os.getenv("PDRFO_LOG_DB_PATH", "pdrfo_logs.db")
    rx_only: bool = _bool_env("RX_ONLY", "true")
    enable_sdr: bool = _bool_env("ENABLE_SDR", "false")
    enable_remote_id: bool = _bool_env("ENABLE_REMOTE_ID", "false")
    enable_wifi_monitor: bool = _bool_env("ENABLE_WIFI_MONITOR", "false")
    enable_hackrf: bool = _bool_env("ENABLE_HACKRF", "false")
    hardware_profile: str = os.getenv("PDRFO_HARDWARE_PROFILE", "simulated")


def load_config() -> Config:
    return Config()
