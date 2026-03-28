# Website Monitoring & Alert System v2

A stronger, portfolio-ready Python automation project that monitors websites for content changes and keyword matches, sends alerts via Telegram and email, stores state in SQLite, captures screenshots on alert, exposes a FastAPI dashboard, and ships with Docker support.

## Features

- Monitor multiple pages from a JSON config
- Playwright-based extraction for JavaScript-heavy sites
- Optional CSS selector targeting per monitor
- SQLite persistence for monitor state and alert history
- Keyword matching with configurable alert modes
- Telegram Bot API alerts
- SMTP email alerts
- Screenshot capture on alert
- FastAPI dashboard with recent alerts and monitor state
- Docker + docker-compose support
- Retry and timeout settings
- Structured logging

## Repository structure

```text
website-monitoring-alert-system-v2/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ monitors.json
├─ run.py
├─ dashboard.py
├─ Dockerfile
├─ docker-compose.yml
└─ app/
   ├─ __init__.py
   ├─ config.py
   ├─ models.py
   ├─ db.py
   ├─ storage.py
   ├─ utils.py
   ├─ fetcher.py
   ├─ dashboard_app.py
   ├─ monitor_service.py
   ├─ templates/
   │  └─ index.html
   └─ notifiers/
      ├─ __init__.py
      ├─ telegram_notifier.py
      └─ email_notifier.py
```

## Setup

### Local

```bash
git clone https://github.com/your-username/website-monitoring-alert-system-v2.git
cd website-monitoring-alert-system-v2
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
python run.py
```

Dashboard:

```bash
uvicorn dashboard:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up --build
```

Monitoring service runs once on container start. Dashboard is available on port `8000`.

## `monitors.json` example

```json
[
  {
    "name": "Remote Python Jobs",
    "url": "https://example.com/jobs",
    "selector": ".job-card",
    "keywords": ["python", "automation", "playwright", "scraping"],
    "alert_on": "keyword_or_change",
    "enabled": true
  }
]
```

## Alert modes

- `change`
- `keyword`
- `keyword_or_change`

## Screenshots

When `SAVE_SCREENSHOT_ON_ALERT=true`, an alerting monitor saves a PNG under `screenshots/`.

## Dashboard

The FastAPI dashboard shows:
- monitors and their last status
- most recent alerts
- recent matched keywords
- screenshot file names when available

## Portfolio summary

Built a production-ready Python monitoring platform that tracks website changes and keyword matches, stores persistent state in SQLite, sends alerts through Telegram and email, captures screenshots on alert, and exposes a FastAPI dashboard for reviewing monitor health and alert history. Designed for job boards, marketplace tracking, product monitoring, and internal business alerts.
