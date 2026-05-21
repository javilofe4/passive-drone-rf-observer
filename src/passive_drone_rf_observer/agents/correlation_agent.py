import time
from collections import deque
from typing import Deque, List
from ..models import RFEvent, AggregatedResult


class Correlator:
    def __init__(self, window_s: float = 2.0, min_events: int = 2):
        self.window_s = window_s
        self.min_events = min_events
        self.buffer: Deque[tuple[RFEvent, float]] = deque()

    def add_event(self, event: RFEvent, score: float) -> AggregatedResult:
        now = event.timestamp
        # store (event, score)
        self.buffer.append((event, score))
        # drop old
        while self.buffer and (now - self.buffer[0][0].timestamp) > self.window_s:
            self.buffer.popleft()

        n = len(self.buffer)
        if n == 0:
            return AggregatedResult(start_ts=now, end_ts=now, probability=0.0, contributing_events=0)

        # aggregate: weighted mean of scores
        total = sum(s for (_e, s) in self.buffer)
        avg = total / n

        # reduce false alarms: require at least min_events or a very high single score
        prob = 0.0
        if n >= self.min_events:
            prob = min(1.0, avg * (1.0 + (n - 1) * 0.1))
        else:
            prob = avg * 0.6

        return AggregatedResult(start_ts=self.buffer[0][0].timestamp, end_ts=self.buffer[-1][0].timestamp, probability=prob, contributing_events=n)
