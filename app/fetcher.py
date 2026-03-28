from __future__ import annotations

import time
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def fetch_page_data(
    url: str,
    selector: str | None,
    timeout_ms: int,
    headless: bool,
    user_agent: str,
    max_retries: int,
    retry_delay_sec: int,
    screenshot_path: str | None = None,
) -> tuple[str, str | None]:
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(1500)

                if screenshot_path:
                    Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=screenshot_path, full_page=True)

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")

            if selector:
                elements = soup.select(selector)
                text = "\n".join(el.get_text(" ", strip=True) for el in elements)
            else:
                body = soup.body
                text = body.get_text(" ", strip=True) if body else soup.get_text(" ", strip=True)

            return text.strip(), screenshot_path
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_delay_sec * attempt)
            else:
                raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Unexpected fetch failure")
