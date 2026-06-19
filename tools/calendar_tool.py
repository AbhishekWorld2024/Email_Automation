import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from tools.gmail_tool import SCOPES


def get_calendar_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)


def extract_meeting_details(client, email):
    prompt = f"""Does this email contain a meeting invite or scheduled event?
If yes, extract the details. If no, reply with: NOT_A_MEETING

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:1000]}

If it IS a meeting, reply in this exact format (nothing else):
TITLE: <meeting title>
DATE: <YYYY-MM-DD>
TIME: <HH:MM in 24hr>
LOCATION: <location or Virtual>

If NOT a meeting, reply with just: NOT_A_MEETING"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def add_to_calendar(email, meeting_text):
    if "NOT_A_MEETING" in meeting_text:
        return False
    try:
        lines = {}
        for line in meeting_text.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                lines[key.strip()] = val.strip()

        date = lines.get("DATE", "")
        time = lines.get("TIME", "09:00")
        title = lines.get("TITLE", email["subject"])
        location = lines.get("LOCATION", "")

        if not date:
            return False

        start_dt = f"{date}T{time}:00"
        service = get_calendar_service()
        event = {
            "summary": title,
            "location": location,
            "description": f"From: {email['from']}\nSubject: {email['subject']}",
            "start": {"dateTime": start_dt, "timeZone": "America/Chicago"},
            "end": {"dateTime": start_dt, "timeZone": "America/Chicago"},
            "reminders": {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": 15}],
            },
        }
        service.events().insert(calendarId="primary", body=event).execute()
        return True
    except Exception as e:
        print(f"Calendar error: {e}")
        return False
