from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class MonitorConfig:
    name: str
    url: str
    selector: str | None = None
    keywords: List[str] = field(default_factory=list)
    alert_on: str = "keyword_or_change"
    enabled: bool = True


@dataclass
class MonitorResult:
    name: str
    url: str
    text: str
    fingerprint: str
    matched_keywords: List[str]
    changed: bool
    should_alert: bool
    reason: str
    screenshot_path: str | None = None
