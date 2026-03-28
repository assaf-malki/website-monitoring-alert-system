from __future__ import annotations

import os
import sqlite3
from typing import Any


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS monitor_state (
                    monitor_name TEXT PRIMARY KEY,
                    fingerprint TEXT,
                    last_reason TEXT,
                    last_checked_at TEXT,
                    last_matched_keywords TEXT,
                    last_screenshot_path TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitor_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    matched_keywords TEXT,
                    preview TEXT,
                    screenshot_path TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_monitor_state(self, monitor_name: str) -> dict[str, Any]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM monitor_state WHERE monitor_name = ?",
                (monitor_name,),
            ).fetchone()
            return dict(row) if row else {}

    def upsert_monitor_state(
        self,
        monitor_name: str,
        fingerprint: str,
        last_reason: str,
        last_checked_at: str,
        last_matched_keywords: str,
        last_screenshot_path: str | None,
    ) -> None:
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO monitor_state (
                    monitor_name, fingerprint, last_reason, last_checked_at,
                    last_matched_keywords, last_screenshot_path
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(monitor_name) DO UPDATE SET
                    fingerprint = excluded.fingerprint,
                    last_reason = excluded.last_reason,
                    last_checked_at = excluded.last_checked_at,
                    last_matched_keywords = excluded.last_matched_keywords,
                    last_screenshot_path = excluded.last_screenshot_path
            """, (
                monitor_name,
                fingerprint,
                last_reason,
                last_checked_at,
                last_matched_keywords,
                last_screenshot_path,
            ))
            conn.commit()

    def insert_alert(
        self,
        monitor_name: str,
        url: str,
        reason: str,
        matched_keywords: str,
        preview: str,
        screenshot_path: str | None,
        created_at: str,
    ) -> None:
        with self.connect() as conn:
            conn.execute("""
                INSERT INTO alerts (
                    monitor_name, url, reason, matched_keywords, preview,
                    screenshot_path, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                monitor_name,
                url,
                reason,
                matched_keywords,
                preview,
                screenshot_path,
                created_at,
            ))
            conn.commit()

    def list_monitor_states(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT * FROM monitor_state
                ORDER BY last_checked_at DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def list_recent_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("""
                SELECT * FROM alerts
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]
