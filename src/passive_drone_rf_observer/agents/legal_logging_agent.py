from ..models import RFEvent, Alert
from ..storage.sqlite_store import SQLiteStore


class LegalLogger:
    def __init__(self, db_path: str | None = None):
        self.store = SQLiteStore(db_path)

    def record_event(self, event: RFEvent, label: str) -> None:
        # Only store minimal metadata. Never store payloads or PII.
        self.store.log_event(event, label)

    def record_alert(self, alert: Alert) -> None:
        self.store.log_alert(alert)
