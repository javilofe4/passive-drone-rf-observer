import random
import time
from typing import Iterator
from .base import RFSource
from ..models import RFEvent, SourceType


class SimulatedRFSource(RFSource):
    """Simple simulated RF events generator."""

    def __init__(self, source_name: str = "simulator", mode: str = "normal"):
        self.source_name = source_name
        self.mode = mode

    def set_mode(self, mode: str) -> None:
        self.mode = mode

    def iter_events(self) -> Iterator[RFEvent]:
        while True:
            ts = time.time()
            band = random.choice([2.4e9, 5.8e9, 915e6, 433e6])
            freq = band + random.uniform(-1e6, 1e6)
            bw = random.choice([200e3, 1e6, 5e6, None])
            rssi = random.uniform(-90.0, -20.0)
            dur = random.uniform(1.0, 500.0)
            notes = None

            if self.mode == "quiet":
                rssi = random.uniform(-95.0, -50.0)
                bw = random.choice([100e3, 300e3, 600e3])
                notes = "quiet"
            elif self.mode == "normal":
                if random.random() < 0.08:
                    rssi = random.uniform(-55.0, -25.0)
                    bw = random.choice([1e6, 2e6, 5e6])
                    dur = random.uniform(5.0, 120.0)
                    notes = "normal burst"
            elif self.mode == "noisy":
                if random.random() < 0.25:
                    rssi = random.uniform(-100.0, -60.0)
                    bw = random.choice([100e3, 300e3, 600e3])
                    notes = "noise"
            elif self.mode == "drone_activity":
                if random.random() < 0.35:
                    band = random.choice([2.4e9, 5.8e9])
                    freq = band + random.uniform(-500e3, 500e3)
                    rssi = random.uniform(-45.0, -15.0)
                    bw = random.choice([1e6, 2e6, 5e6])
                    dur = random.uniform(5.0, 120.0)
                    notes = "drone-like"

            yield RFEvent(
                timestamp=ts,
                frequency_hz=freq,
                bandwidth_hz=bw,
                rssi_dbm=rssi,
                duration_ms=dur,
                source=SourceType.SIMULATED_RF,
                notes=notes,
            )
