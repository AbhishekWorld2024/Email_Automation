import os
import requests


def send_telegram_message(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)


def notify_email(result: dict) -> None:
    priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(result["priority"], "⚪")
    text = (
        f"{priority_emoji} <b>[{result['priority']}] [{result['category']}]</b>\n"
        f"<b>From:</b> {result['from']}\n"
        f"<b>Subject:</b> {result['subject']}\n"
        f"<b>Summary:</b> {result['summary']}"
    )
    send_telegram_message(text)


def notify_digest(new_count: int, skipped: int) -> None:
    send_telegram_message(f"✅ Email Agent done — {new_count} new email(s) processed, {skipped} skipped.")
