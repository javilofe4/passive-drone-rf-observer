from __future__ import annotations
import time
from typing import List
from ..models import (
    WifiEnvironmentEvent,
    WifiEnvironmentEventType,
    WifiObservation,
    SourceType,
)


def analyze_wifi_environment(
    observations: List[WifiObservation],
    known_hashes: set[str],
    last_signals: dict[str, int],
) -> tuple[List[WifiEnvironmentEvent], set[str], dict[str, int]]:
    events: List[WifiEnvironmentEvent] = []
    channel_counts: dict[int, int] = {}
    current_hashes: set[str] = set(known_hashes)
    current_signals: dict[str, int] = dict(last_signals)

    for observation in observations:
        if observation.bssid_hash not in current_hashes:
            events.append(
                WifiEnvironmentEvent(
                    timestamp=observation.timestamp,
                    event_type=WifiEnvironmentEventType.NEW_NETWORK_SEEN,
                    score=0.7,
                    explanation=f"New network seen: {observation.ssid}",
                    source=observation.source,
                )
            )
            current_hashes.add(observation.bssid_hash)

        if observation.signal_percent >= 75:
            events.append(
                WifiEnvironmentEvent(
                    timestamp=observation.timestamp,
                    event_type=WifiEnvironmentEventType.STRONG_SIGNAL_SEEN,
                    score=0.6,
                    explanation=f"Strong Wi-Fi signal seen for {observation.ssid}",
                    source=observation.source,
                )
            )

        previous_signal = current_signals.get(observation.bssid_hash)
        if previous_signal is not None and abs(observation.signal_percent - previous_signal) >= 25:
            delta = observation.signal_percent - previous_signal
            events.append(
                WifiEnvironmentEvent(
                    timestamp=observation.timestamp,
                    event_type=WifiEnvironmentEventType.SIGNAL_CHANGED,
                    score=min(1.0, abs(delta) / 100.0 + 0.2),
                    explanation=f"Signal changed by {delta:+d}% for {observation.ssid}",
                    source=observation.source,
                )
            )

        current_signals[observation.bssid_hash] = observation.signal_percent

        if observation.channel is not None:
            channel_counts[observation.channel] = channel_counts.get(observation.channel, 0) + 1

    for channel, count in channel_counts.items():
        if count >= 5:
            events.append(
                WifiEnvironmentEvent(
                    timestamp=time.time(),
                    event_type=WifiEnvironmentEventType.CROWDED_CHANNEL,
                    score=min(1.0, 0.5 + (count - 4) * 0.1),
                    explanation=f"Channel {channel} has {count} visible networks",
                    source=SourceType.WINDOWS_WIFI_SCAN,
                )
            )

    if not events:
        events.append(
            WifiEnvironmentEvent(
                timestamp=time.time(),
                event_type=WifiEnvironmentEventType.UNKNOWN,
                score=0.1,
                explanation="No notable wireless environment changes detected",
                source=SourceType.WINDOWS_WIFI_SCAN,
            )
        )

    return events, current_hashes, current_signals
