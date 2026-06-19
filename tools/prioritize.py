def prioritize_email(client, email):
    prompt = f"""Rate the urgency of this email as exactly one of:
High | Medium | Low

High = needs action today (deadlines, urgent requests, security alerts)
Medium = should read within a few days
Low = newsletters, promotions, no action needed

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:500]}

Reply with only High, Medium, or Low."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
