from flask import render_template, request, redirect, url_for
import requests
import logging
import os
from . import app
from ..db import Database
from .. import config

# Set up logging
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

@app.route('/health')
def health():
    """Health check endpoint that also verifies environment variables."""
    required_vars = {
        'SLACK_CLIENT_ID': config.SLACK_CLIENT_ID,
        'SLACK_CLIENT_SECRET': config.SLACK_CLIENT_SECRET,
        'SLACK_APP_TOKEN': config.SLACK_APP_TOKEN,
        'GOOGLE_API_KEY': config.GOOGLE_API_KEY,
        'SLACK_SIGNING_SECRET': os.environ.get('SLACK_SIGNING_SECRET')
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        return {
            'status': 'error',
            'missing_env_vars': missing_vars
        }, 500
        
    # Include first few chars of client ID for verification
    safe_client_id = f"{config.SLACK_CLIENT_ID[:6]}..." if config.SLACK_CLIENT_ID else "None"
    
    return {
        'status': 'healthy',
        'database': 'connected',
        'client_id_preview': safe_client_id,
        'env_vars': 'all present'
    }

@app.route('/')
def index():
    """Landing page with 'Add to Slack' button."""
    if not config.SLACK_CLIENT_ID:
        logger.error("SLACK_CLIENT_ID is not set")
        return render_template('error.html', 
                             error="SLACK_CLIENT_ID environment variable is not set. Please configure the application properly.")
    
    # Log the client ID (first few characters for debugging)
    safe_client_id = f"{config.SLACK_CLIENT_ID[:6]}..." if config.SLACK_CLIENT_ID else "None"
    logger.info(f"Using Slack Client ID: {safe_client_id}")
    
    return render_template('index.html', client_id=config.SLACK_CLIENT_ID)

@app.route('/slack/oauth_redirect')
def oauth_redirect():
    """Handle OAuth redirect from Slack."""
    # Get code from request
    code = request.args.get('code')
    if not code:
        return render_template('error.html', error="No code provided")

    # Exchange code for tokens
    try:
        response = requests.post(
            'https://slack.com/api/oauth.v2.access',
            data={
                'code': code,
                'client_id': config.SLACK_CLIENT_ID,
                'client_secret': config.SLACK_CLIENT_SECRET
            }
        ).json()

        if not response.get('ok'):
            error_msg = response.get('error', 'Unknown error')
            logger.error(f"Slack OAuth error: {error_msg}")
            return render_template('error.html', error=f"Slack error: {error_msg}")

        try:
            # Extract all necessary information
            team_id = response['team']['id']
            team_name = response['team']['name']
            bot_token = response['access_token']
            bot_id = response['bot_user_id']

            logger.info(f"Received OAuth tokens for workspace: {team_name} ({team_id})")
            logger.info(f"Bot User ID: {bot_id}")

            # Add workspace to database
            if not db.add_workspace(team_id, team_name, bot_token, bot_id):
                raise Exception("Failed to store workspace in database")

            # Initialize bot for this workspace
            from .. import bot
            bot_instance = bot.SlackBot()
            bot_instance.add_workspace(team_id, team_name, bot_token, bot_id)

            logger.info(f"Successfully set up workspace: {team_name}")
            return render_template('success.html', team_name=team_name)
            
        except KeyError as e:
            logger.error(f"Invalid Slack response: missing {str(e)}")
            logger.error(f"Response data: {response}")
            return render_template('error.html', 
                                error=f"Invalid response from Slack: missing {str(e)}")

    except Exception as e:
        logger.error(f"OAuth error: {str(e)}", exc_info=True)
        return render_template('error.html', error=str(e))
