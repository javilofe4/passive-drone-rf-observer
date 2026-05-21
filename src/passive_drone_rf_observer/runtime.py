from __future__ import annotations
import threading
import time
from typing import Optional

from .config import Config
from .hardware import get_radio_hardware_profile
from .agents.correlation_agent import Correlator
from .agents.legal_logging_agent import LegalLogger
from .pipelines.rf_pipeline import RfPipeline
from .pipelines.wifi_pipeline import WifiPipeline
from .sources.simulated_rf_source import SimulatedRFSource
from .sources.windows_wifi_scan_source import WindowsWifiScanSource
from .state import ObservationState
from .models import SourceType


class AppRuntime:
    MODES = ("quiet", "normal", "noisy", "drone_activity")

    def __init__(self, config: Config):
        self.config = config
        self.mode = "normal"
        self.running = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.state = ObservationState()
        self.logger = LegalLogger(str(self.config.log_db_path))
        self.profile = get_radio_hardware_profile(self.config.hardware_profile)
        self.rf_source = SimulatedRFSource(source_name=self.profile.name, mode=self.mode)
        self.correlator = Correlator(
            window_s=self.config.correlation_window_s,
            min_events=self.config.min_events_for_alert,
        )
        self.rf_pipeline = RfPipeline(self.correlator, self.logger, self.state)
        self.wifi_pipeline = WifiPipeline(
            WindowsWifiScanSource(salt=self.config.wifi_bssid_salt),
            self.logger,
            self.state,
        )
        self._next_wifi_scan_ts = time.time()

    def start(self) -> dict:
        if self.running:
            return self.get_status()

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self.running = True
        self._thread.start()
        return self.get_status()

    def stop(self) -> dict:
        if self.running:
            self._stop_event.set()
            if self._thread is not None:
                self._thread.join(timeout=2.0)
        self.running = False
        return self.get_status()

    def set_mode(self, mode: str) -> dict:
        if mode not in self.MODES:
            raise ValueError(f"Unsupported mode: {mode}")
        with self._lock:
            self.mode = mode
            self.rf_source.set_mode(mode)
        return self.get_status()

    def clear_events(self) -> dict:
        self.state.clear_rf_events()
        return self.get_status()

    def clear_wifi_observations(self) -> dict:
        self.state.clear_wifi_data()
        self.wifi_pipeline.reset()
        return self.get_status()

    def scan_wifi(self) -> list[dict]:
        if not self.config.enable_windows_wifi_scan:
            return []
        return self.wifi_pipeline.scan()

    def get_status(self) -> dict:
        snapshot = self.state.snapshot()
        return {
            "running": self.running,
            "mode": self.mode,
            "num_events_received": snapshot["total_events"],
            "num_drone_like": snapshot["drone_like_events"],
            "last_alert": snapshot["last_alert"],
            "risk_level": snapshot["risk_level"],
            "real_wifi_enabled": self.config.enable_windows_wifi_scan,
            "num_wifi_observations": snapshot["num_wifi_observations"],
            "last_wifi_scan_ts": snapshot["last_wifi_scan_ts"],
            "config": {
                "detection_threshold": self.config.min_events_for_alert,
                "correlation_window_s": self.config.correlation_window_s,
                "event_interval_s": self.config.event_interval_s,
                "log_db_path": str(self.logger.store.path),
                "wifi_scan_interval_s": self.config.wifi_scan_interval_s,
                "enable_windows_wifi_scan": self.config.enable_windows_wifi_scan,
            },
        }

    def get_events(self) -> list[dict]:
        return self.state.get_events()

    def get_alerts(self) -> list[dict]:
        return self.state.get_alerts()

    def get_wifi_observations(self) -> list[dict]:
        return self.state.get_wifi_observations()

    def get_wifi_environment_events(self) -> list[dict]:
        return self.state.get_wifi_environment_events()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            now = time.time()
            if self.config.enable_windows_wifi_scan and now >= self._next_wifi_scan_ts:
                self._next_wifi_scan_ts = now + self.config.wifi_scan_interval_s
                self.scan_wifi()

            try:
                event = next(self.rf_source.iter_events())
            except StopIteration:
                break

            self.rf_pipeline.process_event(event)

            if self._stop_event.wait(self.config.event_interval_s):
                break
