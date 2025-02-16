import logging
from typing import List, Tuple, Dict, Optional
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sqlite3
import os

from .config import SLACK_APP_TOKEN, GOOGLE_API_KEY
from .db import Database
from .llm import LLM

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.db = Database()
        self.model = LLM(API_KEY=GOOGLE_API_KEY, model_name='gemini-pro')
        
        # Initialize single app instance with OAuth
        self.app = App(
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
            installation_store_bot_only=True,
            token=None,  # Don't use a single token in OAuth mode
            authorize=self._authorize  # Add authorize function
        )
        
        # Set up event handlers
        self._setup_handlers()
        
        # Create socket mode handler
        self.handler = SocketModeHandler(self.app, SLACK_APP_TOKEN)
        
    def _authorize(self, enterprise_id: Optional[str], team_id: Optional[str], **kwargs) -> Optional[Dict]:
        """Authorize incoming requests using stored tokens."""
        logger.info(f"Authorizing request for team_id: {team_id}")
        
        if not team_id:
            logger.error("No team_id provided for authorization")
            return None
            
        # Get workspace details from database
        workspace = self.db.get_workspace(team_id)
        if workspace:
            logger.info(f"Found authorization for team {team_id}")
            return {
                "bot_token": workspace["bot_token"],
                "bot_id": workspace.get("bot_id"),
                "team_id": workspace["team_id"]
            }
            
        logger.error(f"No authorization found for team {team_id}")
        return None
        
    def _setup_handlers(self) -> None:
        """Set up event handlers for the Slack bot."""
        @self.app.event("app_mention")
        def handle_mention(event, say, context):
            logger.info(f"Received event: {event}")
            try:
                thread_ts = event.get("thread_ts", event["ts"])
                channel_id = event["channel"]
                user_message = event["text"]
                
                logger.info(f"Received mention: channel={channel_id}, thread={thread_ts}, "
                          f"message={user_message}")
                
                # Get team ID from the event
                team_id = event.get("team_id") or event.get("team")
                if not team_id:
                    raise ValueError("Could not determine team ID from event")
                
                logger.info(f"Processing message for team {team_id}")
                
                # Store user message
                self.db.store_message(channel_id, thread_ts, event["user"], 
                                    user_message, False)
                
                # Get conversation history
                history = self.db.get_thread_history(channel_id, thread_ts)
                logger.info(f"Retrieved history: {history}")
                
                # Convert 'true'/'false' strings back to boolean for formatting
                context = "\n".join([
                    f"{'Bot' if is_bot == 'true' else 'User'}: {msg}" 
                    for msg, is_bot in history
                ])
                
                response = self.model.get_chat_response(context) 
                logger.info(f"Sending response: {response}")
                
                # Store bot response
                self.db.store_message(channel_id, thread_ts, "BOT", response, True)
                
                # Send response
                say(**format_response(response), thread_ts=thread_ts)
                
            except Exception as e:
                logger.error(f"Error in handle_mention: {e}", exc_info=True)
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                say(text=error_msg, thread_ts=thread_ts)

        # Add a message listener for debugging
        @self.app.message("")
        def handle_message(message, say, context):
            logger.info(f"Received message: {message}")

        def format_response(response: str) -> dict:
            return {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 Bot Response",
                            "emoji": True
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": response
                        }
                    }
                ]
            }

    def start(self) -> None:
        """Start the bot."""
        try:
            logger.info("Starting Slack bot...")
            # Log app configuration
            logger.info(f"App Configuration:")
            logger.info(f"  Signing Secret: {'Set' if os.environ.get('SLACK_SIGNING_SECRET') else 'Not Set'}")
            logger.info(f"  App Token: {'Set' if SLACK_APP_TOKEN else 'Not Set'}")
            logger.info(f"  Client ID: {'Set' if os.environ.get('SLACK_CLIENT_ID') else 'Not Set'}")
            logger.info(f"  Client Secret: {'Set' if os.environ.get('SLACK_CLIENT_SECRET') else 'Not Set'}")
            
            # Start the handler
            self.handler.start()
        except Exception as e:
            logger.error(f"Error starting bot: {e}", exc_info=True)
            raise

    def add_workspace(self, team_id: str, team_name: str, bot_token: str, bot_id: str) -> None:
        """Add a new workspace to the database."""
        try:
            if not self.db.add_workspace(team_id, team_name, bot_token, bot_id):
                raise Exception("Failed to store workspace in database")
            logger.info(f"Added workspace to database: {team_id} ({team_name})")
        except Exception as e:
            logger.error(f"Error adding workspace {team_id}: {e}", exc_info=True)
            raise
