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
            
            # Create new memo page with properties
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
            
            page_id = new_page["id"]
            
            # Add detailed content blocks to the page
            try:
                self.notion.blocks.children.append(
                    block_id=page_id,
                    children=[
                        {
                            "object": "block",
                            "type": "heading_2",
                            "heading_2": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": f"📝 Team Work Updates - {weekday}"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        },
                        {
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "🎯 Today's Goals:"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Add your goals here"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        },
                        {
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "✅ Completed Tasks:"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Add completed tasks here"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        },
                        {
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "🚧 In Progress:"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Add in-progress tasks here"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        },
                        {
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "❗ Blockers/Issues:"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Add blockers or issues here"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": []
                            }
                        },
                        {
                            "object": "block",
                            "type": "heading_3",
                            "heading_3": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "💡 Notes:"
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "object": "block",
                            "type": "bulleted_list_item",
                            "bulleted_list_item": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "Add additional notes here"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                )
                logger.info(f"✅ Content blocks added to memo")
            except Exception as block_error:
                logger.warning(f"⚠️ Failed to add content blocks (page created successfully): {block_error}")
            
            logger.info(f"✅ Successfully created today's memo: {title}")
            return page_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create memo: {e}")
            logger.error(f"Error details: {str(e)}")
            return None
    
    def extract_text_from_rich_text(self, rich_text):
        """Extract plain text from rich text objects"""
        if not rich_text:
            return ""
        return "".join([text.get("plain_text", "") for text in rich_text])
    
    def format_blocks_to_text(self, blocks):
        """Convert Notion blocks to readable text format"""
        content = []
        
        for block in blocks:
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                text = self.extract_text_from_rich_text(block["paragraph"]["rich_text"])
                if text.strip():
                    content.append(text)
                else:
                    content.append("")  # Empty line
                    
            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                text = self.extract_text_from_rich_text(block[block_type]["rich_text"])
                if text.strip():
                    content.append(f"\n{text}")
                    
            elif block_type == "bulleted_list_item":
                text = self.extract_text_from_rich_text(block["bulleted_list_item"]["rich_text"])
                if text.strip():
                    content.append(f"• {text}")
                    
            elif block_type == "numbered_list_item":
                text = self.extract_text_from_rich_text(block["numbered_list_item"]["rich_text"])
                if text.strip():
                    content.append(f"1. {text}")
                    
            elif block_type == "to_do":
                text = self.extract_text_from_rich_text(block["to_do"]["rich_text"])
                checked = "☑️" if block["to_do"].get("checked", False) else "☐"
                if text.strip():
                    content.append(f"{checked} {text}")
                    
            elif block_type == "code":
                text = self.extract_text_from_rich_text(block["code"]["rich_text"])
                if text.strip():
                    content.append(f"```\n{text}\n```")
                    
            elif block_type == "quote":
                text = self.extract_text_from_rich_text(block["quote"]["rich_text"])
                if text.strip():
                    content.append(f"> {text}")
                    
        return "\n".join(content)
    
    def get_today_memo_content(self):
        """Get today's memo content including all blocks"""
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
            title = page["properties"]["Title"]["title"][0]["text"]["content"]
            
            # Get all blocks from the page
            blocks_response = self.notion.blocks.children.list(block_id=page_id)
            blocks = blocks_response.get("results", [])
            
            # Convert blocks to readable text
            content = self.format_blocks_to_text(blocks)
            
            if not content.strip():
                content = "No updates have been added to today's memo yet."
            
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

🔗 View full details in Notion: {memo_data["url"]}

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