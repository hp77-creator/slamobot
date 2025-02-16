import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack configuration
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# Database configuration
DB_PATH = "messages.db"

# LLM configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
