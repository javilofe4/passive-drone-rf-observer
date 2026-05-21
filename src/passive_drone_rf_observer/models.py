from dataclasses import dataclass
from typing import Optional


@dataclass
class RFEvent:
    timestamp: float
    frequency_hz: float
    bandwidth_hz: Optional[float]
    rssi_dbm: float
    duration_ms: float
    source: str
    notes: Optional[str] = None


@dataclass
class WifiObservation:
    timestamp: float
    ssid: str
    bssid_hash: str
    signal_percent: int
    channel: Optional[int]
    radio_type: Optional[str]
    authentication: Optional[str]
    source: str = "windows_wifi_scan"
    notes: Optional[str] = None


@dataclass
class WifiEnvironmentEvent:
    timestamp: float
    event_type: str
    score: float
    explanation: str
    source: str = "windows_wifi_scan"


@dataclass
class ClassificationResult:
    label: str
    score: float
    explanation: str


@dataclass
class AggregatedResult:
    start_ts: float
    end_ts: float
    probability: float
    contributing_events: int


@dataclass
class Alert:
    level: str  # none, low, medium, high
    probability: float
    message: str
