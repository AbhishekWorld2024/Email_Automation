def summarize_email(client, email):
    prompt = f"""Summarize this email in 2 sentences. Be direct and factual.
Focus on: what it is about and what action (if any) is needed.

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:1000]}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
