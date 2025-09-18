import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from notion_client import Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyMemoManager:
    def __init__(self):
        self.notion = Client(auth=os.environ["NOTION_TOKEN"])
        self.database_id = os.environ["NOTION_DATABASE_ID"]
        self.team_members = [
            {"name": "Brook", "email": "brook.ma@cvnio.com", "timezone": "Asia/Shanghai"},
            {"name": "Gustavo", "email": "gustavo.paredes@cvnio.com", "timezone": "America/Mexico_City"},
            {"name": "Sunil", "email": "gummalla.sunilreddy@cvnio.com", "timezone": "Asia/Kolkata"},
            {"name": "Moiz", "email": "Moizeali@cvnio.com", "timezone": "Asia/Dubai"}
        ]
        
    def create_daily_memo(self):
        """Create today's memo in Notion"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        title = f"Daily Memo - {today}"
        
        try:
            # Check if today's memo already exists
            existing = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Date",
                    "date": {
                        "equals": today
                    }
                }
            )
            
            if existing["results"]:
                logger.info(f"Today's memo already exists: {title}")
                return existing["results"][0]["id"]
            
            # Create new memo
            new_page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    },
                    "Date": {
                        "date": {
                            "start": today
                        }
                    },
                    "Content": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "Please add today's work updates and progress here..."
                                }
                            }
                        ]
                    }
                }
            )
            
            logger.info(f"Successfully created today's memo: {title}")
            return new_page["id"]
            
        except Exception as e:
            logger.error(f"Failed to create memo: {e}")
            return None
    
    def get_today_memo_content(self):
        """Get today's memo content"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        try:
            results = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Date",
                    "date": {
                        "equals": today
                    }
                }
            )
            
            if not results["results"]:
                logger.warning("No memo found for today")
                return None
            
            page = results["results"][0]
            page_id = page["id"]
            
            # Get page content
            content_prop = page["properties"]["Content"]["rich_text"]
            if content_prop:
                content = "".join([text["text"]["content"] for text in content_prop])
            else:
                content = "No updates for today"
            
            title = page["properties"]["Title"]["title"][0]["text"]["content"]
            
            return {
                "title": title,
                "content": content,
                "url": f"https://notion.so/{page_id.replace('-', '')}"
            }
            
        except Exception as e:
            logger.error(f"Failed to get memo content: {e}")
            return None
    
    def send_daily_summary(self):
        """Send daily summary email"""
        memo_data = self.get_today_memo_content()
        if not memo_data:
            logger.error("Cannot get memo content, canceling email send")
            return False
        
        try:
            # Setup email server
            server = smtplib.SMTP(os.environ["EMAIL_HOST"], int(os.environ["EMAIL_PORT"]))
            server.starttls()
            server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASSWORD"])
            
            # Prepare email content
            subject = f"Team Daily Report - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
            
            for member in self.team_members:
                msg = MIMEMultipart()
                msg['From'] = os.environ["EMAIL_FROM"]
                msg['To'] = member["email"]
                msg['Subject'] = subject
                
                body = f"""
Dear {member["name"]},

Here's today's team work summary:

{memo_data["content"]}

View details: {memo_data["url"]}

---
Sent at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
                
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Send email
                text = msg.as_string()
                server.sendmail(os.environ["EMAIL_FROM"], member["email"], text)
                logger.info(f"Email sent to {member['name']} ({member['email']})")
            
            server.quit()
            logger.info("All emails sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send emails: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python daily_memo.py [create|send]")
        sys.exit(1)
    
    action = sys.argv[1]
    memo_manager = DailyMemoManager()
    
    if action == "create":
        memo_manager.create_daily_memo()
    elif action == "send":
        memo_manager.send_daily_summary()
    else:
        print("Invalid action. Use 'create' or 'send'")
        sys.exit(1)

if __name__ == "__main__":
    main()