from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel


class ConfigSchema(BaseModel):
    detection_threshold: int
    correlation_window_s: float
    event_interval_s: float
    log_db_path: str


class AlertSchema(BaseModel):
    timestamp: float
    level: str
    probability: float
    message: str


class EventSchema(BaseModel):
    timestamp: float
    timestamp_iso: str
    frequency_mhz: float
    rssi_dbm: float
    duration_ms: float
    label: str
    score: float
    explanation: str
    source: str


class StatusResponse(BaseModel):
    running: bool
    mode: str
    num_events_received: int
    num_drone_like: int
    last_alert: Optional[AlertSchema]
    risk_level: str
    config: ConfigSchema


class ModeRequest(BaseModel):
    mode: Literal["quiet", "normal", "noisy", "drone_activity"]
