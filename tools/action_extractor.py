import json
from pathlib import Path
from datetime import datetime

ACTIONS_FILE = Path("memory/action_items.json")


def extract_action_items(client, email):
    prompt = f"""Extract action items, deadlines, and tasks from this email.
Return a JSON array only. Each item: {{"task": "...", "deadline": "YYYY-MM-DD or null", "priority": "high/medium/low"}}
If no action items exist, return: []

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:800]}

Return only valid JSON, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        text = response.content[0].text.strip()
        # Extract JSON array if wrapped in markdown code block
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except Exception:
        return []


def save_action_items(email, items):
    if not items:
        return
    ACTIONS_FILE.parent.mkdir(exist_ok=True)
    existing = json.loads(ACTIONS_FILE.read_text()) if ACTIONS_FILE.exists() else []
    for item in items:
        item["from_email"] = email["from"]
        item["email_subject"] = email["subject"]
        item["added_on"] = datetime.now().strftime("%Y-%m-%d")
    existing.extend(items)
    ACTIONS_FILE.write_text(json.dumps(existing, indent=2))
