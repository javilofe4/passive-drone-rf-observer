from abc import ABC, abstractmethod
from typing import Iterator
from ..models import RFEvent


class RFSource(ABC):
    """Abstract RF source. Implementations should yield RFEvent objects."""

    @abstractmethod
    def iter_events(self) -> Iterator[RFEvent]:
        raise NotImplementedError
