import json
import os
from pathlib import Path
from tools.gmail_tool import fetch_emails
from tools.classify import classify_email
from tools.prioritize import prioritize_email
from tools.summarize import summarize_email
from tools.email_digest import send_email_digest
from tools.telegram_tool import notify_email, notify_digest
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

MEMORY_FILE = Path("memory/history.json")
MEMORY_FILE.parent.mkdir(exist_ok=True)


def load_history():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text())
    return []


def save_history(history):
    MEMORY_FILE.write_text(json.dumps(history, indent=2))


def run_agent():
    print("Fetching new emails...\n")
    emails = fetch_emails(limit=10)
    history = load_history()
    processed_ids = {h["id"] for h in history}

    new_results = []
    for email in emails:
        if email["id"] in processed_ids:
            continue

        print(f"Processing: {email['subject'][:60]}...")
        category = classify_email(client, email)
        priority = prioritize_email(client, email)
        summary = summarize_email(client, email)

        result = {
            "id": email["id"],
            "subject": email["subject"],
            "from": email["from"],
            "category": category,
            "priority": priority,
            "summary": summary,
        }

        history.append(result)

        if category == "Spam":
            print(f"[SKIPPED — Spam]  {email['subject']}")
            continue

        new_results.append(result)

        print(f"[{priority}] [{category}]  {email['subject']}")
        print(f"From    : {email['from']}")
        print(f"Summary : {summary}")
        print("-" * 60)

        # Telegram — silent if blocked (e.g. PythonAnywhere free tier)
        try:
            notify_email(result)
        except Exception:
            pass

    save_history(history)
    skipped = len(emails) - len(new_results)
    print(f"\nDone. Processed {len(new_results)} new email(s) (skipped {skipped} already seen).")

    if new_results:
        send_email_digest(new_results)
        print("Email digest sent to abhishek.arugonda223@gmail.com")

    try:
        notify_digest(len(new_results), skipped)
    except Exception:
        pass


if __name__ == "__main__":
    run_agent()
