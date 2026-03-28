from __future__ import annotations

import logging
from typing import List

from app.config import settings
from app.db import Database
from app.fetcher import fetch_page_data
from app.models import MonitorConfig, MonitorResult
from app.notifiers.email_notifier import EmailNotifier
from app.notifiers.telegram_notifier import TelegramNotifier
from app.storage import StateStore
from app.utils import (
    content_fingerprint,
    ensure_dir,
    load_json_file,
    preview_text,
    safe_filename,
    setup_logging,
    utc_now_iso,
)


MONITORS_FILE = "monitors.json"


def load_monitors() -> List[MonitorConfig]:
    raw = load_json_file(MONITORS_FILE)
    if not isinstance(raw, list):
        raise ValueError("monitors.json must contain a list")

    monitors: List[MonitorConfig] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        monitors.append(
            MonitorConfig(
                name=str(item.get("name", "")).strip(),
                url=str(item.get("url", "")).strip(),
                selector=item.get("selector"),
                keywords=[str(k).strip() for k in item.get("keywords", []) if str(k).strip()],
                alert_on=str(item.get("alert_on", "keyword_or_change")).strip(),
                enabled=bool(item.get("enabled", True)),
            )
        )

    return [m for m in monitors if m.name and m.url and m.enabled]


def evaluate_monitor(monitor: MonitorConfig, text: str, previous_fingerprint: str | None) -> MonitorResult:
    current_fingerprint = content_fingerprint(text)
    changed = previous_fingerprint is not None and previous_fingerprint != current_fingerprint

    text_lower = text.lower()
    matched_keywords = [kw for kw in monitor.keywords if kw.lower() in text_lower]

    alert_mode = monitor.alert_on.lower()
    keyword_hit = bool(matched_keywords)

    if alert_mode == "change":
        should_alert = changed
        reason = "content_changed" if changed else "no_change"
    elif alert_mode == "keyword":
        should_alert = keyword_hit
        reason = "keyword_match" if keyword_hit else "no_keyword_match"
    else:
        should_alert = changed or keyword_hit
        if changed and keyword_hit:
            reason = "keyword_match_and_content_changed"
        elif changed:
            reason = "content_changed"
        elif keyword_hit:
            reason = "keyword_match"
        else:
            reason = "no_match"

    return MonitorResult(
        name=monitor.name,
        url=monitor.url,
        text=text,
        fingerprint=current_fingerprint,
        matched_keywords=matched_keywords,
        changed=changed,
        should_alert=should_alert,
        reason=reason,
    )


def build_alert_message(result: MonitorResult) -> str:
    keywords_line = ", ".join(result.matched_keywords) if result.matched_keywords else "None"
    screenshot_line = result.screenshot_path or "None"
    return (
        f"Website Monitor Alert v2\n\n"
        f"Monitor: {result.name}\n"
        f"URL: {result.url}\n"
        f"Reason: {result.reason}\n"
        f"Matched Keywords: {keywords_line}\n"
        f"Changed: {'yes' if result.changed else 'no'}\n"
        f"Screenshot: {screenshot_line}\n"
        f"Time: {utc_now_iso()}\n\n"
        f"Preview:\n{preview_text(result.text)}"
    )


def main() -> None:
    setup_logging()

    ensure_dir(settings.screenshots_dir)

    db = Database(settings.sqlite_db_path)
    store = StateStore(db)

    telegram = TelegramNotifier(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
    )
    email = EmailNotifier(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        from_email=settings.smtp_from,
        to_email=settings.smtp_to,
    )

    monitors = load_monitors()
    logging.info("Loaded %s monitor(s)", len(monitors))

    for monitor in monitors:
        state_key = monitor.name
        logging.info("Checking: %s", monitor.name)

        try:
            previous = store.get_monitor_state(state_key)
            previous_fingerprint = previous.get("fingerprint")

            screenshot_path = None
            if settings.save_screenshot_on_alert:
                screenshot_path = f"{settings.screenshots_dir}/{safe_filename(monitor.name)}.png"

            text, actual_screenshot_path = fetch_page_data(
                url=monitor.url,
                selector=monitor.selector,
                timeout_ms=settings.request_timeout_sec * 1000,
                headless=settings.headless,
                user_agent=settings.user_agent,
                max_retries=settings.max_retries,
                retry_delay_sec=settings.retry_delay_sec,
                screenshot_path=screenshot_path,
            )

            result = evaluate_monitor(monitor, text, previous_fingerprint)
            result.screenshot_path = actual_screenshot_path if result.should_alert else None

            if result.should_alert:
                message = build_alert_message(result)
                telegram.send(message)
                email.send(
                    subject=f"Website Monitor Alert: {result.name}",
                    body=message,
                    attachment_path=result.screenshot_path,
                )
                db.insert_alert(
                    monitor_name=result.name,
                    url=result.url,
                    reason=result.reason,
                    matched_keywords=", ".join(result.matched_keywords),
                    preview=preview_text(result.text),
                    screenshot_path=result.screenshot_path,
                    created_at=utc_now_iso(),
                )
                logging.info("Alert sent for: %s", monitor.name)
            else:
                logging.info("No alert for: %s (%s)", monitor.name, result.reason)

            store.set_monitor_state(
                key=state_key,
                fingerprint=result.fingerprint,
                last_reason=result.reason,
                last_checked_at=utc_now_iso(),
                last_matched_keywords=result.matched_keywords,
                last_screenshot_path=result.screenshot_path,
            )

        except Exception as exc:
            logging.exception("Failed monitor '%s': %s", monitor.name, exc)

    logging.info("Done")
