#!/usr/bin/env python3
"""Telegram group + topic routing helper used by all assistant scripts."""

import requests
from pathlib import Path
from dotenv import dotenv_values

config = dotenv_values(Path.home() / ".env")

TOKEN    = config.get("TELEGRAM_BOT_TOKEN")
GROUP_ID = config.get("TELEGRAM_GROUP_ID")

TOPICS = {
    "chat":   int(config.get("TELEGRAM_TOPIC_CHAT",   11)),
    "emails": int(config.get("TELEGRAM_TOPIC_EMAILS", 12)),
    "jobs":   int(config.get("TELEGRAM_TOPIC_JOBS",   13)),
    "stocks": int(config.get("TELEGRAM_TOPIC_STOCKS", 15)),
    "daily":  int(config.get("TELEGRAM_TOPIC_DAILY",  14)),
}


def send(text, topic="chat", parse_mode="Markdown", reply_markup=None):
    """Send a message to a specific topic in the group."""
    payload = {
        "chat_id":           GROUP_ID,
        "text":              text,
        "parse_mode":        parse_mode,
        "message_thread_id": TOPICS.get(topic, TOPICS["chat"]),
    }
    if reply_markup:
        import json
        payload["reply_markup"] = json.dumps(reply_markup)
    resp = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)
    return resp.ok


def send_chat(text, **kwargs):   return send(text, "chat",   **kwargs)
def send_emails(text, **kwargs): return send(text, "emails", **kwargs)
def send_jobs(text, **kwargs):   return send(text, "jobs",   **kwargs)
def send_stocks(text, **kwargs): return send(text, "stocks", **kwargs)
def send_daily(text, **kwargs):  return send(text, "daily",  **kwargs)
