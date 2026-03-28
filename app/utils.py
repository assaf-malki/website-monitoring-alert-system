from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_fingerprint(text: str) -> str:
    normalized = " ".join((text or "").split()).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def preview_text(text: str, limit: int = 400) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def load_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    value = value.strip("._")
    return value or "monitor"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
