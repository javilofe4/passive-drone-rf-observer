from __future__ import annotations
import threading
import time
from collections import deque
from pathlib import Path
from typing import Deque, Dict, List, Optional

from .agents.alert_agent import evaluate_alert
from .agents.correlation_agent import Correlator
from .agents.detector_agent import classify_event
from .agents.legal_logging_agent import LegalLogger
from .agents.wifi_environment_agent import analyze_wifi_environment
from .config import Config, load_config
from .hardware import get_radio_hardware_profile
from .models import RFEvent, WifiObservation
from .sources.simulated_rf_source import SimulatedRFSource
from .sources.windows_wifi_scan_source import WindowsWifiScanSource


class SimulationManager:
    MODES = ("quiet", "normal", "noisy", "drone_activity")

    def __init__(self, config: Optional[Config] = None):
        self.config = config or load_config()
        self.mode = "normal"
        self.running = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._event_iter = None
        self._reset_state()
        self._init_simulation()

    def _reset_state(self) -> None:
        self.total_events = 0
        self.drone_like_events = 0
        self.events: Deque[Dict] = deque(maxlen=200)
        self.alerts: Deque[Dict] = deque(maxlen=100)
        self.wifi_observations: Deque[Dict] = deque(maxlen=200)
        self.wifi_environment_events: Deque[Dict] = deque(maxlen=100)
        self.wifi_hashes_seen: set[str] = set()
        self.wifi_last_signals: dict[str, int] = {}
        self.last_wifi_scan_ts: Optional[float] = None
        self.last_alert_level = "none"
        self.risk_level = "none"

    def _init_simulation(self) -> None:
        self.profile = get_radio_hardware_profile(self.config.hardware_profile)
        self.source = SimulatedRFSource(source_name=self.profile.name, mode=self.mode)
        self.wifi_source = WindowsWifiScanSource(salt=self.config.wifi_bssid_salt)
        self.correlator = Correlator(
            window_s=self.config.correlation_window_s,
            min_events=self.config.min_events_for_alert,
        )
        self.logger = LegalLogger()
        self._event_iter = self.source.iter_events()
        self._next_wifi_scan_ts = time.time()

    def start(self) -> Dict:
        if self.running:
            return self.get_status()

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self.running = True
        self._thread.start()
        return self.get_status()

    def stop(self) -> Dict:
        if self.running:
            self._stop_event.set()
            if self._thread is not None:
                self._thread.join(timeout=2.0)
        self.running = False
        return self.get_status()

    def set_mode(self, mode: str) -> Dict:
        if mode not in self.MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        with self._lock:
            self.mode = mode
            self.source.set_mode(mode)
        return self.get_status()

    def clear_events(self) -> Dict:
        with self._lock:
            self.events.clear()
            self.total_events = 0
            self.drone_like_events = 0
            self.last_alert_level = "none"
            self.risk_level = "none"
        return self.get_status()

    def get_status(self) -> Dict:
        with self._lock:
            latest_alert = self.alerts[0] if self.alerts else None
            return {
                "running": self.running,
                "mode": self.mode,
                "num_events_received": self.total_events,
                "num_drone_like": self.drone_like_events,
                "last_alert": latest_alert,
                "risk_level": self.risk_level,
                "real_wifi_enabled": self.config.enable_windows_wifi_scan,
                "num_wifi_observations": len(self.wifi_observations),
                "last_wifi_scan_ts": self.last_wifi_scan_ts,
                "config": {
                    "detection_threshold": self.config.min_events_for_alert,
                    "correlation_window_s": self.config.correlation_window_s,
                    "event_interval_s": self.config.event_interval_s,
                    "log_db_path": self.logger.store.path,
                    "wifi_scan_interval_s": self.config.wifi_scan_interval_s,
                    "enable_windows_wifi_scan": self.config.enable_windows_wifi_scan,
                },
            }

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

    def clear_wifi_observations(self) -> Dict:
        with self._lock:
            self.wifi_observations.clear()
            self.wifi_environment_events.clear()
            self.last_wifi_scan_ts = None
        return self.get_status()

    def scan_wifi(self) -> List[Dict]:
        if not self.config.enable_windows_wifi_scan:
            return []
        observations = self.wifi_source.scan()
        entries = []
        wifi_objs = []
        for observation in observations:
            wifi_objs.append(observation)
            entry = {
                "timestamp": observation.timestamp,
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(observation.timestamp)),
                "ssid": observation.ssid,
                "bssid_hash": observation.bssid_hash,
                "signal_percent": observation.signal_percent,
                "channel": observation.channel,
                "radio_type": observation.radio_type,
                "authentication": observation.authentication,
                "source": observation.source,
            }
            entries.append(entry)

        events, self.wifi_hashes_seen, self.wifi_last_signals = analyze_wifi_environment(
            wifi_objs,
            self.wifi_hashes_seen,
            self.wifi_last_signals,
        )
        with self._lock:
            self.wifi_observations = deque(entries, maxlen=200)
            self.wifi_environment_events = deque(
                [
                    {
                        "timestamp": event.timestamp,
                        "event_type": event.event_type,
                        "score": event.score,
                        "explanation": event.explanation,
                        "source": event.source,
                    }
                    for event in events
                ],
                maxlen=100,
            )
            self.last_wifi_scan_ts = time.time()
        return list(self.wifi_observations)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            current_time = time.time()
            if self.config.enable_windows_wifi_scan and current_time >= self._next_wifi_scan_ts:
                self._next_wifi_scan_ts = current_time + self.config.wifi_scan_interval_s
                self.scan_wifi()

            try:
                event = next(self._event_iter)
            except StopIteration:
                break
            classification = classify_event(event)
            aggregated = self.correlator.add_event(event, classification.score)
            alert = evaluate_alert(aggregated.probability)
            self.logger.record_event(event, classification.label)
            if alert.level != "none":
                self.logger.record_alert(alert)

            self._append_event(event, classification)
            if alert.level != "none":
                self._append_alert(alert)

            self.last_alert_level = alert.level
            self.risk_level = alert.level

            if self._stop_event.wait(self.config.event_interval_s):
                break

    def _append_event(self, event: RFEvent, classification) -> None:
        entry = {
            "timestamp": event.timestamp,
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)),
            "frequency_mhz": round(event.frequency_hz / 1e6, 3),
            "rssi_dbm": event.rssi_dbm,
            "duration_ms": event.duration_ms,
            "label": classification.label,
            "score": classification.score,
            "explanation": classification.explanation,
            "source": event.source,
        }
        with self._lock:
            self.events.appendleft(entry)
            self.total_events += 1
            if classification.label == "drone_like":
                self.drone_like_events += 1

    def _append_alert(self, alert) -> None:
        entry = {
            "timestamp": time.time(),
            "level": alert.level,
            "probability": alert.probability,
            "message": alert.message,
        }
        with self._lock:
            self.alerts.appendleft(entry)
