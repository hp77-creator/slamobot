import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

def log_env_vars():
    """Log all environment variables (with sensitive data masked)."""
    logger.info("Environment Variables:")
    for key in sorted(os.environ):
        value = os.environ[key]
        # Mask sensitive values
        if any(secret in key.lower() for secret in ['token', 'key', 'secret', 'password']):
            masked_value = value[:6] + "..." if value else "Not set"
        else:
            masked_value = value
        logger.info(f"  {key}: {masked_value}")

# Load environment variables
load_dotenv()
log_env_vars()

def get_required_env(key: str) -> str:
    """Get a required environment variable or log an error."""
    value = os.environ.get(key)
    if not value:
        logger.error(f"Required environment variable {key} is not set")
    else:
        logger.info(f"Loaded {key} environment variable")
    return value

# Slack configuration
SLACK_BOT_TOKEN = get_required_env("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = get_required_env("SLACK_APP_TOKEN")
SLACK_CLIENT_ID = get_required_env("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = get_required_env("SLACK_CLIENT_SECRET")
SLACK_SIGNING_SECRET = get_required_env("SLACK_SIGNING_SECRET")

# Database configuration
DB_PATH = os.environ.get("DB_PATH", "messages.db")
logger.info(f"Using database path: {DB_PATH}")

# LLM configuration
GOOGLE_API_KEY = get_required_env("GOOGLE_API_KEY")

# Validate required configuration
REQUIRED_VARS = [
    SLACK_BOT_TOKEN,
    SLACK_APP_TOKEN,
    SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET,
    SLACK_SIGNING_SECRET,
    GOOGLE_API_KEY
]

if not all(REQUIRED_VARS):
    missing = [
        var for var, value in {
            "SLACK_BOT_TOKEN": SLACK_BOT_TOKEN,
            "SLACK_APP_TOKEN": SLACK_APP_TOKEN,
            "SLACK_CLIENT_ID": SLACK_CLIENT_ID,
            "SLACK_CLIENT_SECRET": SLACK_CLIENT_SECRET,
            "SLACK_SIGNING_SECRET": SLACK_SIGNING_SECRET,
            "GOOGLE_API_KEY": GOOGLE_API_KEY
        }.items() if not value
    ]
    logger.error(f"Missing required environment variables: {', '.join(missing)}")
else:
    logger.info("All required environment variables are set")
