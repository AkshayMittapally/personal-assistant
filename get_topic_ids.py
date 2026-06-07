#!/usr/bin/env python3
"""
Helper to discover the Group Chat ID and Topic Thread IDs.
Run after creating the group and sending one message in each topic.
"""

import requests
from pathlib import Path
from dotenv import dotenv_values

config = dotenv_values(Path.home() / ".env")
TOKEN  = config.get("TELEGRAM_BOT_TOKEN")

resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10)
updates = resp.json().get("result", [])

if not updates:
    print("No updates found. Send a message in your group first, then re-run.")
else:
    seen = {}
    for u in updates:
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat", {})
        chat_id   = chat.get("id")
        chat_type = chat.get("type")
        chat_name = chat.get("title") or chat.get("username") or chat.get("first_name")
        thread_id = msg.get("message_thread_id")
        text      = msg.get("text", "")[:40]
        forum     = chat.get("is_forum", False)

        key = (chat_id, thread_id)
        if key not in seen:
            seen[key] = True
            print(f"Chat: {chat_name!r} ({chat_type}) | chat_id={chat_id} | thread_id={thread_id} | forum={forum} | text={text!r}")
