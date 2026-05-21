from __future__ import annotations
from typing import Optional
from pathlib import Path
from pydantic import BaseModel

from ..models import (
    AlertLevel,
    RfClassification,
    SourceType,
    WifiEnvironmentEventType,
)


class ConfigSchema(BaseModel):
    detection_threshold: int
    correlation_window_s: float
    event_interval_s: float
    log_db_path: str
    wifi_scan_interval_s: float
    enable_windows_wifi_scan: bool


class AlertSchema(BaseModel):
    timestamp: float
    level: AlertLevel
    probability: float
    message: str
    source: SourceType


class EventSchema(BaseModel):
    timestamp: float
    timestamp_iso: str
    frequency_mhz: float
    rssi_dbm: float
    duration_ms: float
    label: RfClassification
    score: float
    explanation: str
    source: SourceType


class WifiObservationSchema(BaseModel):
    timestamp: float
    timestamp_iso: str
    ssid: str
    bssid_hash: str
    signal_percent: int
    channel: Optional[int]
    radio_type: Optional[str]
    authentication: Optional[str]
    source: SourceType


class WifiEnvironmentEventSchema(BaseModel):
    timestamp: float
    event_type: WifiEnvironmentEventType
    score: float
    explanation: str
    source: SourceType


class StatusResponse(BaseModel):
    running: bool
    mode: str
    num_events_received: int
    num_drone_like: int
    last_alert: Optional[AlertSchema]
    risk_level: str
    real_wifi_enabled: bool
    num_wifi_observations: int
    last_wifi_scan_ts: Optional[float]
    config: ConfigSchema


class ModeRequest(BaseModel):
    mode: str
