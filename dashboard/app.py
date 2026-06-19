import json
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request

sys.path.append(str(Path(__file__).parent.parent))

app = Flask(__name__)

HISTORY_FILE = Path(__file__).parent.parent / "memory/history.json"
ACTIONS_FILE = Path(__file__).parent.parent / "memory/action_items.json"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/emails")
def get_emails():
    category = request.args.get("category", "")
    priority = request.args.get("priority", "")
    emails = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []
    if category:
        emails = [e for e in emails if e.get("category") == category]
    if priority:
        emails = [e for e in emails if e.get("priority") == priority]
    emails.reverse()
    return jsonify(emails)


@app.route("/api/actions")
def get_actions():
    actions = json.loads(ACTIONS_FILE.read_text()) if ACTIONS_FILE.exists() else []
    actions.reverse()
    return jsonify(actions)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
