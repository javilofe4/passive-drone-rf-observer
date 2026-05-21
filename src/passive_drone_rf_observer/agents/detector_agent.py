from typing import Tuple
from ..models import RFEvent, ClassificationResult


def classify_event(event: RFEvent) -> ClassificationResult:
    """Simple heuristic classifier.

    Returns a label among: noise, wifi_like, drone_like, unknown
    and a score between 0.0 and 1.0 with a short explanation.
    """
    score = 0.0
    label = "unknown"
    explanation = "no strong indicators"

    # strong signal and moderate bandwidth often used by control links
    if event.rssi_dbm > -50 and (event.bandwidth_hz or 0) >= 1e6:
        score = min(1.0, ( -40 - event.rssi_dbm) / -40 + 0.6)
        label = "drone_like"
        explanation = "strong narrow-to-medium bandwidth burst"
    # common WiFi bands and medium bandwidth
    elif 2.3e9 < event.frequency_hz < 2.5e9 or 5.6e9 < event.frequency_hz < 5.9e9:
        if event.bandwidth_hz and event.bandwidth_hz >= 1e6:
            score = 0.6
            label = "wifi_like"
            explanation = "frequency and bandwidth consistent with WiFi"
    # very weak signals -> noise
    if event.rssi_dbm < -85:
        score = 0.05
        label = "noise"
        explanation = "very low RSSI, likely noise"

    return ClassificationResult(label=label, score=max(0.0, min(1.0, score)), explanation=explanation)
