def classify_email(client, email):
    prompt = f"""Classify this email into exactly one category:
Work | Personal | Spam | Newsletter | Finance | Support

Subject: {email['subject']}
From: {email['from']}
Body: {email['body'][:500]}

Reply with only the category name, nothing else."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
