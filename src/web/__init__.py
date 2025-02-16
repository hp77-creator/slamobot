import logging
from flask import Flask
from .. import config

# Set up logging
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask app
app.config.update(
    SLACK_CLIENT_ID=config.SLACK_CLIENT_ID,
    SLACK_CLIENT_SECRET=config.SLACK_CLIENT_SECRET
)

# Log configuration status
if app.config['SLACK_CLIENT_ID'] and app.config['SLACK_CLIENT_SECRET']:
    logger.info("Flask app configured with Slack OAuth credentials")
else:
    logger.error("Flask app missing Slack OAuth credentials")

from . import routes  # Import routes after app creation to avoid circular imports
