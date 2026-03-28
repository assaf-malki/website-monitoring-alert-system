from __future__ import annotations

import json
from app.db import Database


class StateStore:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_monitor_state(self, key: str) -> dict:
        return self.db.get_monitor_state(key)

    def set_monitor_state(
        self,
        key: str,
        fingerprint: str,
        last_reason: str,
        last_checked_at: str,
        last_matched_keywords: list[str],
        last_screenshot_path: str | None,
    ) -> None:
        self.db.upsert_monitor_state(
            monitor_name=key,
            fingerprint=fingerprint,
            last_reason=last_reason,
            last_checked_at=last_checked_at,
            last_matched_keywords=json.dumps(last_matched_keywords, ensure_ascii=False),
            last_screenshot_path=last_screenshot_path,
        )
