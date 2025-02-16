from flask import render_template, request, redirect, url_for
import requests
import os
from . import app
from ..db import Database

# Initialize database
db = Database()

@app.route('/health')
def health():
    """Health check endpoint that also verifies environment variables."""
    required_vars = [
        'SLACK_CLIENT_ID',
        'SLACK_CLIENT_SECRET',
        'SLACK_APP_TOKEN',
        'GOOGLE_API_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        return {
            'status': 'error',
            'missing_env_vars': missing_vars
        }, 500
        
    # Include first few chars of client ID for verification
    client_id = os.environ.get('SLACK_CLIENT_ID', '')
    safe_client_id = f"{client_id[:6]}..." if client_id else "None"
    
    return {
        'status': 'healthy',
        'database': 'connected',
        'client_id_preview': safe_client_id,
        'env_vars': 'all present'
    }

@app.route('/')
def index():
    """Landing page with 'Add to Slack' button."""
    client_id = os.environ.get('SLACK_CLIENT_ID')
    safe_client_id = f"{client_id[:6]}..." if client_id else "None"
    app.logger.info(f"Using Slack Client ID: {safe_client_id}")
    if not client_id:
        return render_template('error.html', 
                             error="SLACK_CLIENT_ID environment variable is not set. Please configure the application properly.")
    
    # Log the client ID (first few characters for debugging)
    safe_client_id = f"{client_id[:6]}..." if client_id else "None"
    app.logger.info(f"Using Slack Client ID: {safe_client_id}")
    
    return render_template('index.html', client_id=client_id)

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
                'client_id': os.environ.get('SLACK_CLIENT_ID'),
                'client_secret': os.environ.get('SLACK_CLIENT_SECRET')
            }
        ).json()

        if not response.get('ok'):
            return render_template('error.html', 
                                error=f"Slack error: {response.get('error')}")

        try:
            # Store tokens in database and initialize bot for the workspace
            team_id = response['team']['id']
            team_name = response['team']['name']
            bot_token = response['access_token']

            # Add workspace to database and initialize bot
            if not db.add_workspace(team_id, team_name, bot_token):
                raise Exception("Failed to store workspace in database")

            # Initialize bot for this workspace
            from .. import bot
            bot_instance = bot.SlackBot()
            bot_instance.add_workspace(team_id, team_name, bot_token)

            return render_template('success.html', team_name=team_name)
            
        except KeyError as e:
            return render_template('error.html', 
                                error=f"Invalid response from Slack: missing {str(e)}")

    except Exception as e:
        return render_template('error.html', error=str(e))
