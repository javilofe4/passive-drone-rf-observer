from __future__ import annotations
from typing import List, Optional

from ..models import (
    Alert,
    AlertLevel,
    SourceType,
    WifiEnvironmentEvent,
    WifiEnvironmentEventType,
)


def evaluate_alert(aggregated_prob: float, source: SourceType = SourceType.SIMULATED_RF) -> Alert:
    if aggregated_prob < 0.2:
        level = AlertLevel.NONE
    elif aggregated_prob < 0.5:
        level = AlertLevel.LOW
    elif aggregated_prob < 0.75:
        level = AlertLevel.MEDIUM
    else:
        level = AlertLevel.HIGH

    message = f"Aggregated probability of unusual RF activity: {aggregated_prob:.2f}"
    return Alert(level=level, probability=aggregated_prob, message=message, source=source)


def evaluate_wifi_alert(events: List[WifiEnvironmentEvent]) -> Optional[Alert]:
    noteworthy = [event for event in events if event.event_type != WifiEnvironmentEventType.UNKNOWN]
    if not noteworthy:
        return None

    strong_signals = sum(
        1 for event in events if event.event_type == WifiEnvironmentEventType.STRONG_SIGNAL_SEEN
    )
    crowded = any(event.event_type == WifiEnvironmentEventType.CROWDED_CHANNEL for event in events)

    if crowded or strong_signals >= 2:
        level = AlertLevel.MEDIUM
        probability = 0.6
        message = "Repeated strong local wireless activity detected"
    else:
        level = AlertLevel.LOW
        probability = 0.35
        message = "Wireless activity of interest detected"

    return Alert(level=level, probability=probability, message=message, source=SourceType.WINDOWS_WIFI_SCAN)
