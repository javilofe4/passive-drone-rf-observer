from __future__ import annotations
import time
from ..agents.alert_agent import evaluate_wifi_alert
from ..agents.legal_logging_agent import LegalLogger
from ..agents.wifi_environment_agent import analyze_wifi_environment
from ..models import AlertLevel, SourceType, WifiObservation
from ..sources.windows_wifi_scan_source import WindowsWifiScanSource
from ..state import ObservationState


class WifiPipeline:
    def __init__(
        self,
        wifi_source: WindowsWifiScanSource,
        logger: LegalLogger,
        state: ObservationState,
    ):
        self.wifi_source = wifi_source
        self.logger = logger
        self.state = state
        self.known_hashes: set[str] = set()
        self.last_signals: dict[str, int] = {}

    def scan(self) -> list[dict]:
        observations = self.wifi_source.scan()
        events, self.known_hashes, self.last_signals = analyze_wifi_environment(
            observations,
            self.known_hashes,
            self.last_signals,
        )

        scan_ts = time.time()
        observation_entries = [
            {
                "timestamp": obs.timestamp,
                "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(obs.timestamp)),
                "ssid": obs.ssid,
                "bssid_hash": obs.bssid_hash,
                "signal_percent": obs.signal_percent,
                "channel": obs.channel,
                "radio_type": obs.radio_type,
                "authentication": obs.authentication,
                "source": obs.source.value if isinstance(obs.source, SourceType) else obs.source,
            }
            for obs in observations
        ]
        environment_entries = [
            {
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "score": event.score,
                "explanation": event.explanation,
                "source": event.source.value if isinstance(event.source, SourceType) else event.source,
            }
            for event in events
        ]

        self.state.update_wifi_data(observation_entries, environment_entries, scan_ts)

        wifi_alert = evaluate_wifi_alert(events)
        if wifi_alert and wifi_alert.level != AlertLevel.NONE:
            self.logger.record_alert(wifi_alert)
            self.state.append_alert(
                {
                    "timestamp": time.time(),
                    "level": wifi_alert.level.value,
                    "probability": wifi_alert.probability,
                    "message": wifi_alert.message,
                    "source": wifi_alert.source.value,
                }
            )

        return observation_entries

    def reset(self) -> None:
        self.known_hashes.clear()
        self.last_signals.clear()
