import base64
from email.mime.text import MIMEText
from tools.gmail_tool import get_gmail_service


def create_draft_reply(client, email):
    prompt = f"""Write a professional, concise reply to this email in 2-3 sentences.
Be helpful and direct. Do not add subject or greeting — just the reply body.

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:800]}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    reply_text = response.content[0].text.strip()

    service = get_gmail_service()
    msg = MIMEText(reply_text)
    msg["to"] = email["from"]
    msg["subject"] = f"Re: {email['subject']}"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()
    return reply_text
