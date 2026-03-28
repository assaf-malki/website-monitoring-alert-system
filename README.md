# Website Monitoring & Alert System

A Python-based system for monitoring websites, detecting content changes or keyword matches, and delivering real-time alerts through multiple channels.

The system is designed to handle modern, JavaScript-heavy websites using Playwright, persist monitoring state and history in SQLite, capture screenshots when relevant changes occur, and provide a lightweight dashboard for visibility and tracking.

## Features

* Monitor multiple pages from a JSON configuration
* Playwright-based extraction for dynamic websites
* Optional CSS selector targeting per monitor
* SQLite persistence for state and alert history
* Keyword matching with configurable alert modes
* Telegram notifications via Bot API
* Email notifications via SMTP (with optional attachments)
* Screenshot capture on alert
* FastAPI dashboard for monitoring status and history
* Docker and docker-compose support
* Retry handling and configurable timeouts
* Structured logging

## Repository structure

```
website-monitoring-alert-system/
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

## monitors.json example

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

* `change`
* `keyword`
* `keyword_or_change`

## Screenshots

When `SAVE_SCREENSHOT_ON_ALERT=true`, an alerting monitor saves a PNG under `screenshots/`.

## Dashboard

The FastAPI dashboard provides:

* Current status of all monitors
* Last evaluation results and reasons
* Recent alerts and matched keywords
* Access to captured screenshots (when available)
