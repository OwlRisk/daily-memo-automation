# Daily Memo Automation

Automated daily memo creation and email notification system for distributed teams.

## Features

- Creates daily memo entries in Notion database
- Sends email summaries to team members
- Timezone-aware scheduling
- Automated GitHub Actions workflow

## Setup

### 1. Notion Configuration

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy the Integration Token
3. Create a database with these properties:
   - Title (Title type)
   - Date (Date type) 
   - Content (Text type)
4. Share the database with your integration

### 2. GitHub Secrets

Set these repository secrets: