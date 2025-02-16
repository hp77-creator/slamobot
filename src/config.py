import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack configuration
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_CLIENT_ID = os.environ.get("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET")

# Database configuration
DB_PATH = os.environ.get("DB_PATH", "messages.db")

# LLM configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
