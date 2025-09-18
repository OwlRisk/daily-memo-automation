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
        weekday = datetime.now(timezone.utc).strftime("%A")
        title = f"Daily Memo - {today} ({weekday})"
        
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
                                    "content": f"📝 Team Work Updates - {weekday}\n\n🎯 Today's Goals:\n• \n\n✅ Completed Tasks:\n• \n\n🚧 In Progress:\n• \n\n❗ Blockers/Issues:\n• \n\n💡 Notes:\n• "
                                }
                            }
                        ]
                    }
                }
            )
            
            logger.info(f"✅ Successfully created today's memo: {title}")
            return new_page["id"]
            
        except Exception as e:
            logger.error(f"❌ Failed to create memo: {e}")
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
                logger.warning("⚠️ No memo found for today")
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
            logger.error(f"❌ Failed to get memo content: {e}")
            return None
    
    def send_daily_summary(self):
        """Send daily summary email"""
        memo_data = self.get_today_memo_content()
        if not memo_data:
            logger.error("❌ Cannot get memo content, canceling email send")
            return False
        
        try:
            # Setup email server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("info@cvnio.com", os.environ["EMAIL_PASSWORD"])
            
            # Get current time info
            now_utc = datetime.now(timezone.utc)
            today = now_utc.strftime("%Y-%m-%d")
            weekday = now_utc.strftime("%A")
            
            # Check if weekend
            is_weekend = weekday in ['Saturday', 'Sunday']
            weekend_note = " 🌅" if is_weekend else ""
            
            # Prepare email content
            subject = f"Daily Team Report - {today} ({weekday}){weekend_note}"
            
            success_count = 0
            for member in self.team_members:
                msg = MIMEMultipart()
                msg['From'] = "info@cvnio.com"
                msg['To'] = member["email"]
                msg['Subject'] = subject
                
                # Get local time for this member
                if member["timezone"] == "Asia/Shanghai":
                    local_time = (now_utc + timedelta(hours=8)).strftime('%H:%M')
                elif member["timezone"] == "Asia/Dubai":
                    local_time = (now_utc + timedelta(hours=4)).strftime('%H:%M')
                elif member["timezone"] == "Asia/Kolkata":
                    local_time = (now_utc + timedelta(hours=5, minutes=30)).strftime('%H:%M')
                elif member["timezone"] == "America/Mexico_City":
                    local_time = (now_utc - timedelta(hours=6)).strftime('%H:%M')
                else:
                    local_time = now_utc.strftime('%H:%M UTC')
                
                weekend_greeting = "\n🌅 Weekend Update - Hope you're having a great time!" if is_weekend else ""
                
                body = f"""Hello {member["name"]}! 👋
{weekend_greeting}

📋 Here's today's team work summary:

{memo_data["content"]}

🔗 View full details: {memo_data["url"]}

⏰ Your local time: {local_time}
📅 Report generated: {now_utc.strftime('%Y-%m-%d %H:%M:%S')} UTC

---
🤖 Automated Daily Report System
💌 Team Communication Hub
"""
                
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Send email
                text = msg.as_string()
                server.sendmail("info@cvnio.com", member["email"], text)
                logger.info(f"📧 Email sent to {member['name']} ({member['email']})")
                success_count += 1
            
            server.quit()
            logger.info(f"✅ All emails sent successfully ({success_count}/{len(self.team_members)})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send emails: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python daily_memo.py [create|send]")
        sys.exit(1)
    
    action = sys.argv[1]
    memo_manager = DailyMemoManager()
    
    if action == "create":
        logger.info("🚀 Starting daily memo creation...")
        memo_manager.create_daily_memo()
    elif action == "send":
        logger.info("📤 Starting daily summary email...")
        memo_manager.send_daily_summary()
    else:
        print("❌ Invalid action. Use 'create' or 'send'")
        sys.exit(1)

if __name__ == "__main__":
    main()