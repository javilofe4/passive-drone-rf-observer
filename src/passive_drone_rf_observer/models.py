from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AlertLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceType(str, Enum):
    SIMULATED_RF = "simulated_rf"
    WINDOWS_WIFI_SCAN = "windows_wifi_scan"
    MANUAL_OBSERVATION = "manual_observation"


class RfClassification(str, Enum):
    NOISE = "noise"
    WIFI_LIKE = "wifi_like"
    DRONE_LIKE = "drone_like"
    UNKNOWN = "unknown"


class WifiEnvironmentEventType(str, Enum):
    NEW_NETWORK_SEEN = "new_network_seen"
    NETWORK_DISAPPEARED = "network_disappeared"
    STRONG_SIGNAL_SEEN = "strong_signal_seen"
    SIGNAL_CHANGED = "signal_changed"
    CROWDED_CHANNEL = "crowded_channel"
    UNKNOWN = "unknown"


@dataclass
class RFEvent:
    timestamp: float
    frequency_hz: float
    bandwidth_hz: Optional[float]
    rssi_dbm: float
    duration_ms: float
    source: SourceType
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
    source: SourceType = SourceType.WINDOWS_WIFI_SCAN
    notes: Optional[str] = None


@dataclass
class WifiEnvironmentEvent:
    timestamp: float
    event_type: WifiEnvironmentEventType
    score: float
    explanation: str
    source: SourceType = SourceType.WINDOWS_WIFI_SCAN


@dataclass
class ClassificationResult:
    label: RfClassification
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
    level: AlertLevel
    probability: float
    message: str
    source: SourceType = SourceType.SIMULATED_RF
