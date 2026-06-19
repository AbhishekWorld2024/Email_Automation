import base64
from email.mime.text import MIMEText
from tools.gmail_tool import get_gmail_service

TO_EMAIL = "abhishek.arugonda223@gmail.com"

PRIORITY_COLOR = {"High": "#dc2626", "Medium": "#d97706", "Low": "#16a34a"}


def _build_html(results: list) -> str:
    rows = ""
    for r in results:
        color = PRIORITY_COLOR.get(r["priority"], "#6b7280")
        rows += f"""
        <tr>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;">
            <span style="background:{color};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;">{r['priority']}</span>
            <span style="background:#e0e7ff;color:#3730a3;padding:2px 8px;border-radius:12px;font-size:12px;margin-left:4px;">{r['category']}</span>
          </td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;font-weight:600;">{r['subject']}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;color:#6b7280;font-size:13px;">{r['from']}</td>
          <td style="padding:10px;border-bottom:1px solid #e5e7eb;font-size:13px;">{r['summary']}</td>
        </tr>"""

    return f"""
    <html><body style="font-family:system-ui,sans-serif;max-width:900px;margin:0 auto;padding:20px;">
      <h2 style="color:#111;">📧 Email Agent — Digest</h2>
      <p style="color:#6b7280;">{len(results)} new email(s) processed</p>
      <table style="width:100%;border-collapse:collapse;margin-top:16px;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:10px;text-align:left;font-size:12px;color:#6b7280;">PRIORITY / CATEGORY</th>
            <th style="padding:10px;text-align:left;font-size:12px;color:#6b7280;">SUBJECT</th>
            <th style="padding:10px;text-align:left;font-size:12px;color:#6b7280;">FROM</th>
            <th style="padding:10px;text-align:left;font-size:12px;color:#6b7280;">SUMMARY</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </body></html>"""


def send_email_digest(results: list) -> None:
    if not results:
        return
    service = get_gmail_service()
    html = _build_html(results)
    msg = MIMEText(html, "html")
    msg["to"] = TO_EMAIL
    msg["from"] = TO_EMAIL
    msg["subject"] = f"📧 Email Digest — {len(results)} new email(s)"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
