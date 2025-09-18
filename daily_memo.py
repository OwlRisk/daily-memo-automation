# daily_memo.py
import os
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = [
    "brook.ma@cvnio.com",
    "gustavo.paredes@cvnio.com",
    "gummalla.sunilreddy@cvnio.com",
    "Moizeali@cvnio.com"
]

def get_today_memo():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    query = {"filter": {"property": "Date", "date": {"equals": today}}}
    res = requests.post(url, headers=headers, json=query)
    res.raise_for_status()
    results = res.json()["results"]
    if not results:
        return "No memo found."
    content = results[0]["properties"]["Content"]["rich_text"]
    return "".join([c["text"]["content"] for c in content]) or "No content yet."

def send_email(content):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = "Daily Memo Summary"
    msg.attach(MIMEText(content, "plain"))

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("Email sent.")

def create_tomorrow_memo():
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": f"Daily Memo - {tomorrow}"}}]},
            "Date": {"date": {"start": tomorrow}},
            "Content": {"rich_text": [{"text": {"content": ""}}]}
        }
    }
    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    print("New Daily Memo created:", res.json()["id"])

if __name__ == "__main__":
    memo = get_today_memo()
    send_email(memo)
    create_tomorrow_memo()
