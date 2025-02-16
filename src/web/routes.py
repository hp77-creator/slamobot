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

        # Store tokens in database
        team_id = response['team']['id']
        team_name = response['team']['name']
        bot_token = response['access_token']

        # Update database schema if needed
        with db.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS workspaces
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id TEXT UNIQUE,
                team_name TEXT,
                bot_token TEXT,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')
            
            # Insert or update workspace
            c.execute('''
                INSERT OR REPLACE INTO workspaces (team_id, team_name, bot_token)
                VALUES (?, ?, ?)
            ''', (team_id, team_name, bot_token))
            conn.commit()

        return render_template('success.html', team_name=team_name)

    except Exception as e:
        return render_template('error.html', error=str(e))
