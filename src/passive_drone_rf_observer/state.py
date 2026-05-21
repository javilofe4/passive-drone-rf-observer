from __future__ import annotations
import threading
from collections import deque
from typing import Deque, Dict, List, Optional


class ObservationState:
    def __init__(
        self,
        max_events: int = 200,
        max_alerts: int = 100,
        max_wifi_observations: int = 200,
        max_wifi_environment_events: int = 100,
    ):
        self._lock = threading.Lock()
        self._max_events = max_events
        self._max_alerts = max_alerts
        self._max_wifi_observations = max_wifi_observations
        self._max_wifi_environment_events = max_wifi_environment_events
        self.events: Deque[Dict] = deque(maxlen=self._max_events)
        self.alerts: Deque[Dict] = deque(maxlen=self._max_alerts)
        self.wifi_observations: Deque[Dict] = deque(maxlen=self._max_wifi_observations)
        self.wifi_environment_events: Deque[Dict] = deque(maxlen=self._max_wifi_environment_events)
        self.total_events = 0
        self.drone_like_events = 0
        self.last_wifi_scan_ts: Optional[float] = None
        self.last_alert_level: str = "none"
        self.risk_level: str = "none"

    def append_rf_event(self, event: Dict, is_drone_like: bool = False) -> None:
        with self._lock:
            self.events.appendleft(event)
            self.total_events += 1
            if is_drone_like:
                self.drone_like_events += 1

    def append_alert(self, alert: Dict) -> None:
        with self._lock:
            self.alerts.appendleft(alert)
            self.last_alert_level = alert.get("level", "none")
            self.risk_level = self.last_alert_level

    def update_wifi_data(self, observations: List[Dict], environment_events: List[Dict], scan_ts: float) -> None:
        with self._lock:
            self.wifi_observations = deque(observations, maxlen=self._max_wifi_observations)
            self.wifi_environment_events = deque(environment_events, maxlen=self._max_wifi_environment_events)
            self.last_wifi_scan_ts = scan_ts

    def clear_rf_events(self) -> None:
        with self._lock:
            self.events.clear()
            self.total_events = 0
            self.drone_like_events = 0
            self.last_alert_level = "none"
            self.risk_level = "none"

    def clear_wifi_data(self) -> None:
        with self._lock:
            self.wifi_observations.clear()
            self.wifi_environment_events.clear()
            self.last_wifi_scan_ts = None

    def get_events(self) -> List[Dict]:
        with self._lock:
            return list(self.events)

    def get_alerts(self) -> List[Dict]:
        with self._lock:
            return list(self.alerts)

    def get_wifi_observations(self) -> List[Dict]:
        with self._lock:
            return list(self.wifi_observations)

    def get_wifi_environment_events(self) -> List[Dict]:
        with self._lock:
            return list(self.wifi_environment_events)

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            return {
                "total_events": self.total_events,
                "drone_like_events": self.drone_like_events,
                "last_alert": self.alerts[0] if self.alerts else None,
                "risk_level": self.risk_level,
                "num_wifi_observations": len(self.wifi_observations),
                "last_wifi_scan_ts": self.last_wifi_scan_ts,
            }
