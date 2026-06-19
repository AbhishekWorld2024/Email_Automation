# Deploy to PythonAnywhere (Free Cloud)

## Step 1 — Create free account
Go to https://www.pythonanywhere.com → Sign up (free "Beginner" plan)

## Step 2 — Upload your files
In PythonAnywhere dashboard → Files tab → Upload these files:
- agent.py
- tools/ (entire folder)
- requirements.txt
- .env
- credentials.json
- token.json        ← IMPORTANT: copy from your laptop after running agent.py locally

Directory structure on PythonAnywhere:
/home/yourusername/email-agent/
├── agent.py
├── tools/
├── .env
├── credentials.json
├── token.json
├── memory/          ← create this folder manually
└── requirements.txt

## Step 3 — Install dependencies
In PythonAnywhere → Consoles tab → Bash console:

```bash
cd ~/email-agent
pip install --user -r requirements.txt
```

## Step 4 — Test it manually
```bash
cd ~/email-agent
python agent.py
```
You should get Telegram messages on your phone.

## Step 5 — Schedule it to run every hour
Dashboard → Tasks tab → Add a new scheduled task:
- Command: `cd /home/yourusername/email-agent && python agent.py`
- Hour: Every hour (or pick specific times like 8am, 12pm, 6pm)

Done! The agent now runs automatically without your laptop.
