from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_to: str = os.getenv("SMTP_TO", "")

    request_timeout_sec: int = int(os.getenv("REQUEST_TIMEOUT_SEC", "45"))
    headless: bool = _get_bool("HEADLESS", True)
    state_file: str = os.getenv("STATE_FILE", "data/state.json")
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/monitoring.db")
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay_sec: int = int(os.getenv("RETRY_DELAY_SEC", "2"))
    save_screenshot_on_alert: bool = _get_bool("SAVE_SCREENSHOT_ON_ALERT", True)
    screenshots_dir: str = os.getenv("SCREENSHOTS_DIR", "screenshots")
    user_agent: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    )


settings = Settings()
