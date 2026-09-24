import json
import os
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup

BLOG_FEED_URL = "https://telegram.org/blog/rss?setln=ru"
DUROV_CHANNEL_URL = "https://t.me/durov"


def clean_text(value):
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def load_items(data_file):
    if not data_file.exists():
        return []
    with data_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_blog_items():
    feed = feedparser.parse(BLOG_FEED_URL)
    items = []
    for entry in feed.entries:
        published = entry.get("published", entry.get("updated", ""))
        items.append(
            {
                "id": entry.get("id", entry.get("link", "")),
                "title": clean_text(entry.get("title", "Без названия")),
                "summary": clean_text(entry.get("summary", "")),
                "url": entry.get("link", "https://telegram.org/blog?setln=ru"),
                "source": "Telegram Blog",
                "source_label": "Официальный блог",
                "published": published,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def read_durov_items():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_hash:
        return []

    try:
        from telethon.sync import TelegramClient
    except ImportError:
        return []

    items = []
    session = os.getenv("TELEGRAM_SESSION", "telegram_news")
    with TelegramClient(session, int(api_id), api_hash) as client:
        for message in client.iter_messages("durov", limit=20):
            text = (message.message or "").strip()
            if not text:
                continue
            items.append(
                {
                    "id": f"durov-{message.id}",
                    "title": text.splitlines()[0][:120],
                    "summary": text,
                    "url": f"{DUROV_CHANNEL_URL}/{message.id}",
                    "source": "@durov",
                    "source_label": "Канал Павла Дурова",
                    "published": message.date.isoformat() if message.date else "",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
            )
    return items


def refresh_news(data_file):
    current = load_items(data_file)
    by_id = {item["id"]: item for item in current}
    fetched = read_blog_items() + read_durov_items()
    for item in fetched:
        by_id[item["id"]] = item

    combined = sorted(
        by_id.values(),
        key=lambda item: item.get("published", item.get("fetched_at", "")),
        reverse=True,
    )[:100]
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with data_file.open("w", encoding="utf-8") as file:
        json.dump(combined, file, ensure_ascii=False, indent=2)
    return combined
