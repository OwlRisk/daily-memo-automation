# Daily Memo Automation 🤖

Automated daily memo creation and email notification system for distributed teams.

## 🎯 Features

- ✅ Creates daily memo entries in Notion database
- 📧 Sends email summaries to all team members  
- 🌍 Timezone-aware for global teams
- 📅 Runs 7 days a week (including weekends)
- 🔄 Automated GitHub Actions workflow

## ⏰ Schedule

### Daily Automation (Every Day Including Weekends)
- **02:00 UTC** (10:00 Beijing) - Creates daily memo
- **14:00 UTC** (22:00 Beijing) - Sends email summary

### Local Times
| Team Member | Create Memo | Email Summary |
|-------------|-------------|---------------|
| Brook (Beijing) | 10:00 AM | 10:00 PM |
| Gustavo (Mexico) | 8:00 PM (prev day) | 8:00 AM |
| Sunil (India) | 7:30 AM | 7:30 PM |
| Moiz (Dubai) | 6:00 AM | 6:00 PM |

## 🚀 Setup

### 1. Notion Configuration
1. Create integration at https://www.notion.so/my-integrations
2. Create database with properties:
   - **Title** (Title type)
   - **Date** (Date type)
   - **Content** (Text type)
3. Share database with your integration

### 2. GitHub Secrets
Add these repository secrets: