from typing import Iterator
from ..models import RFEvent


def run_sensor(source) -> Iterator[RFEvent]:
    """Yield events from a source (abstracted)."""
    for ev in source.iter_events():
        yield ev
