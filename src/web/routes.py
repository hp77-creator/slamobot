from flask import render_template, request, redirect, url_for
import requests
import os
from . import app
from ..db import Database

# Initialize database
db = Database()

@app.route('/')
def index():
    """Landing page with 'Add to Slack' button."""
    client_id = os.environ.get('SLACK_CLIENT_ID')
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
