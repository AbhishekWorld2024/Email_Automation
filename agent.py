import json
import os
import sys
from pathlib import Path

# Fix Unicode output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from tools.gmail_tool import fetch_emails
from tools.classify import classify_email
from tools.prioritize import prioritize_email
from tools.summarize import summarize_email
from tools.email_digest import send_email_digest
from tools.telegram_tool import notify_email, notify_digest
from tools.calendar_tool import extract_meeting_details, add_to_calendar
from tools.draft_reply import create_draft_reply
from tools.label_tool import apply_label
from tools.action_extractor import extract_action_items, save_action_items
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

        # Skip Spam entirely
        if category == "Spam":
            print(f"[SKIPPED — Spam]  {email['subject']}")
            continue

        new_results.append(result)
        print(f"[{priority}] [{category}]  {email['subject']}")
        print(f"From    : {email['from']}")
        print(f"Summary : {summary}")

        # Feature 1 — Calendar: detect meeting invites
        try:
            meeting_text = extract_meeting_details(client, email)
            if "NOT_A_MEETING" not in meeting_text:
                added = add_to_calendar(email, meeting_text)
                if added:
                    print(f"  📅 Added to Google Calendar")
        except Exception as e:
            print(f"  Calendar warning: {e}")

        # Feature 2 — Draft reply for High-priority emails
        if priority == "High":
            try:
                draft = create_draft_reply(client, email)
                print(f"  ✍️  Draft reply saved in Gmail")
            except Exception as e:
                print(f"  Draft error: {e}")

        # Feature 3 — Auto-label newsletters
        if category == "Newsletter":
            try:
                apply_label(email["id"], "Auto-Newsletter")
                print(f"  🏷️  Labelled: Auto-Newsletter")
            except Exception as e:
                print(f"  Label error: {e}")

        # Feature 5 — Extract action items
        items = extract_action_items(client, email)
        if items:
            save_action_items(email, items)
            print(f"  ✅ {len(items)} action item(s) saved")

        # Telegram notification
        try:
            notify_email(result)
        except Exception as e:
            print(f"  Telegram warning: {e}")

        print("-" * 60)

    save_history(history)
    skipped = len(emails) - len(new_results)
    print(f"\nDone. Processed {len(new_results)} new email(s) (skipped {skipped} already seen).")

    if new_results:
        send_email_digest(new_results)
        print("Email digest sent.")

    try:
        notify_digest(len(new_results), skipped)
    except Exception as e:
        print(f"Telegram warning: {e}")


if __name__ == "__main__":
    run_agent()
