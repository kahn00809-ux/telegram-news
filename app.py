import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template

from fetcher import refresh_news

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "news.json"
app = Flask(__name__)


def read_news():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def refresh_in_background():
    try:
        refresh_news(DATA_FILE)
    except Exception as error:
        app.logger.warning("News refresh failed: %s", error)


@app.get("/")
def index():
    return render_template("index.html", news=read_news())


@app.get("/api/news")
def api_news():
    return jsonify(read_news())


@app.post("/api/refresh")
def api_refresh():
    refresh_in_background()
    return jsonify(read_news())


def start_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    interval = int(os.getenv("REFRESH_INTERVAL_MINUTES", "30"))
    scheduler.add_job(refresh_in_background, "interval", minutes=interval)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    scheduler = start_scheduler()
    try:
        app.run(debug=True, use_reloader=False)
    finally:
        scheduler.shutdown()
