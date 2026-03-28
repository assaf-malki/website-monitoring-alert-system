from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import Database

app = FastAPI(title="Website Monitoring Dashboard")
templates = Jinja2Templates(directory="app/templates")
app.mount("/screenshots", StaticFiles(directory=settings.screenshots_dir), name="screenshots")


@app.get("/")
def index(request: Request):
    db = Database(settings.sqlite_db_path)
    states = db.list_monitor_states()
    alerts = db.list_recent_alerts(limit=50)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "states": states,
            "alerts": alerts,
        },
    )
