import sqlite3
import time
from pathlib import Path
from typing import Optional
from ..models import Alert, RFEvent


class SQLiteStore:
    def __init__(self, path: Optional[Path | str] = None):
        self.path = Path(path) if path is not None else Path("pdrfo_logs.db")
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL,
                frequency REAL,
                bandwidth REAL,
                rssi REAL,
                duration REAL,
                source TEXT,
                label TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL,
                level TEXT,
                probability REAL,
                message TEXT,
                source TEXT
            )
            """
        )
        self._conn.commit()

    def log_event(self, event: RFEvent, label: str):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO events (ts, frequency, bandwidth, rssi, duration, source, label) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                event.timestamp,
                event.frequency_hz,
                event.bandwidth_hz or 0.0,
                event.rssi_dbm,
                event.duration_ms,
                event.source.value if hasattr(event.source, "value") else event.source,
                label.value if hasattr(label, "value") else label,
            ),
        )
        self._conn.commit()

    def log_alert(self, alert: Alert):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO alerts (ts, level, probability, message, source) VALUES (?, ?, ?, ?, ?)",
            (
                time.time(),
                alert.level.value if hasattr(alert.level, "value") else alert.level,
                alert.probability,
                alert.message,
                alert.source.value if hasattr(alert.source, "value") else alert.source,
            ),
        )
        self._conn.commit()
