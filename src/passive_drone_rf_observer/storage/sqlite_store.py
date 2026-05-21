import sqlite3
from typing import Optional
from pathlib import Path
from ..models import RFEvent, Alert


class SQLiteStore:
    def __init__(self, path: Optional[str] = None):
        self.path = path or "pdrfo_logs.db"
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
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
                message TEXT
            )
            """
        )
        self._conn.commit()

    def log_event(self, event: RFEvent, label: str):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO events (ts, frequency, bandwidth, rssi, duration, source, label) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event.timestamp, event.frequency_hz, event.bandwidth_hz or 0.0, event.rssi_dbm, event.duration_ms, event.source, label),
        )
        self._conn.commit()

    def log_alert(self, alert: Alert):
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO alerts (ts, level, probability, message) VALUES (?, ?, ?, ?)",
            (__import__("time").time(), alert.level, alert.probability, alert.message),
        )
        self._conn.commit()
