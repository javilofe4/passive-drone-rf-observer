from __future__ import annotations
import time
from ..agents.correlation_agent import Correlator
from ..agents.detector_agent import classify_event
from ..agents.alert_agent import evaluate_alert
from ..agents.legal_logging_agent import LegalLogger
from ..models import AlertLevel, RFEvent, RfClassification, SourceType
from ..state import ObservationState


class RfPipeline:
    def __init__(self, correlator: Correlator, logger: LegalLogger, state: ObservationState):
        self.correlator = correlator
        self.logger = logger
        self.state = state

    def process_event(self, event: RFEvent) -> None:
        classification = classify_event(event)
        aggregated = self.correlator.add_event(event, classification.score)
        alert = evaluate_alert(aggregated.probability, source=SourceType.SIMULATED_RF)

        self.logger.record_event(event, classification.label)
        if alert.level != AlertLevel.NONE:
            self.logger.record_alert(alert)

        event_entry = {
            "timestamp": event.timestamp,
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)),
            "frequency_mhz": round(event.frequency_hz / 1e6, 3),
            "rssi_dbm": event.rssi_dbm,
            "duration_ms": event.duration_ms,
            "label": classification.label.value,
            "score": classification.score,
            "explanation": classification.explanation,
            "source": event.source.value if isinstance(event.source, SourceType) else event.source,
        }

        self.state.append_rf_event(
            event_entry,
            is_drone_like=(classification.label == RfClassification.DRONE_LIKE),
        )

        if alert.level != AlertLevel.NONE:
            self.state.append_alert(
                {
                    "timestamp": time.time(),
                    "level": alert.level.value,
                    "probability": alert.probability,
                    "message": alert.message,
                    "source": alert.source.value,
                }
            )
