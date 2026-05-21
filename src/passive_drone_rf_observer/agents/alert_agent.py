from ..models import Alert


def evaluate_alert(aggregated_prob: float, source: str = "simulated_rf") -> Alert:
    if aggregated_prob < 0.2:
        level = "none"
    elif aggregated_prob < 0.5:
        level = "low"
    elif aggregated_prob < 0.75:
        level = "medium"
    else:
        level = "high"

    message = f"Aggregated probability of unusual RF activity: {aggregated_prob:.2f}"
    return Alert(level=level, probability=aggregated_prob, message=message, source=source)


from ..models import WifiEnvironmentEvent


def evaluate_wifi_alert(events: list[WifiEnvironmentEvent]) -> Alert | None:
    noteworthy = [event for event in events if event.event_type != "unknown"]
    if not noteworthy:
        return None

    strong_signals = sum(1 for event in events if event.event_type == "strong_signal_seen")
    crowded = any(event.event_type == "crowded_channel" for event in events)

    if crowded or strong_signals >= 2:
        level = "medium"
        probability = 0.6
        message = "Repeated strong local wireless activity detected"
    else:
        level = "low"
        probability = 0.35
        message = "Wireless activity of interest detected"

    return Alert(level=level, probability=probability, message=message, source="windows_wifi_scan")
