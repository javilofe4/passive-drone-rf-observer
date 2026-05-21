from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os


def _bool_env(env: Mapping[str, str], key: str, default: str = "false") -> bool:
    return str(env.get(key, default)).strip().lower() in ("1", "true", "yes")


def _int_env(env: Mapping[str, str], key: str, default: str) -> int:
    return int(env.get(key, default))


def _float_env(env: Mapping[str, str], key: str, default: str) -> float:
    return float(env.get(key, default))


def _str_env(env: Mapping[str, str], key: str, default: str) -> str:
    return str(env.get(key, default)).strip()


@dataclass(frozen=True)
class Config:
    simulation_duration_s: int
    event_interval_s: float
    correlation_window_s: float
    min_events_for_alert: int
    log_db_path: Path
    rx_only: bool
    enable_sdr: bool
    enable_remote_id: bool
    enable_wifi_monitor: bool
    enable_hackrf: bool
    enable_windows_wifi_scan: bool
    wifi_scan_interval_s: float
    wifi_bssid_salt: str
    hardware_profile: str


def load_config(env: Mapping[str, str] | None = None) -> Config:
    env = env or os.environ
    return Config(
        simulation_duration_s=_int_env(env, "PDRFO_SIM_DURATION", "6"),
        event_interval_s=_float_env(env, "PDRFO_EVENT_INTERVAL", "0.25"),
        correlation_window_s=_float_env(env, "PDRFO_CORRELATION_WINDOW", "2.0"),
        min_events_for_alert=_int_env(env, "PDRFO_MIN_EVENTS", "2"),
        log_db_path=Path(_str_env(env, "PDRFO_LOG_DB_PATH", "pdrfo_logs.db")).expanduser(),
        rx_only=_bool_env(env, "RX_ONLY", "true"),
        enable_sdr=_bool_env(env, "ENABLE_SDR", "false"),
        enable_remote_id=_bool_env(env, "ENABLE_REMOTE_ID", "false"),
        enable_wifi_monitor=_bool_env(env, "ENABLE_WIFI_MONITOR", "false"),
        enable_hackrf=_bool_env(env, "ENABLE_HACKRF", "false"),
        enable_windows_wifi_scan=_bool_env(env, "ENABLE_WINDOWS_WIFI_SCAN", "false"),
        wifi_scan_interval_s=_float_env(env, "WIFI_SCAN_INTERVAL_S", "5.0"),
        wifi_bssid_salt=_str_env(env, "WIFI_BSSID_SALT", "local-dev-salt"),
        hardware_profile=_str_env(env, "PDRFO_HARDWARE_PROFILE", "simulated"),
    )
