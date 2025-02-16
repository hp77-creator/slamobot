import logging
from typing import List, Tuple, Dict
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sqlite3

from .config import SLACK_APP_TOKEN, GOOGLE_API_KEY
from .db import Database
from .llm import LLM

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.db = Database()
        self.model = LLM(API_KEY=GOOGLE_API_KEY, model_name='gemini-pro')
        self.workspace_apps: Dict[str, App] = {}
        self.handlers: Dict[str, SocketModeHandler] = {}
        self._initialize_workspaces()
        
    def _initialize_workspaces(self) -> None:
        """Initialize apps for all workspaces in the database."""
        try:
            with self.db.get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT team_id, bot_token FROM workspaces')
                workspaces = c.fetchall()
                
                for team_id, bot_token in workspaces:
                    self._setup_workspace(team_id, bot_token)
        except sqlite3.Error as e:
            logger.error(f"Database error during workspace initialization: {e}")
            raise

    def _setup_workspace(self, team_id: str, bot_token: str) -> None:
        """Set up a Slack app instance for a specific workspace."""
        try:
            app = App(token=bot_token)
            self._setup_handlers(app)
            self.workspace_apps[team_id] = app
            
            # Create and store handler
            handler = SocketModeHandler(app, SLACK_APP_TOKEN)
            self.handlers[team_id] = handler
            
            logger.info(f"Set up workspace: {team_id}")
        except Exception as e:
            logger.error(f"Error setting up workspace {team_id}: {e}")
            raise

    def _setup_handlers(self, app: App) -> None:
        """Set up event handlers for the Slack bot."""
        @app.event("app_mention")
        def handle_mention(event, say):
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
                logger.error(f"Error in handle_mention: {e}")
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                say(text=error_msg, thread_ts=thread_ts)

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
        """Start all workspace handlers."""
        try:
            logger.info("Starting Slack bot handlers...")
            for team_id, handler in self.handlers.items():
                handler.start()
        except Exception as e:
            logger.error(f"Error starting bot handlers: {e}")
            raise

    def add_workspace(self, team_id: str, bot_token: str) -> None:
        """Add a new workspace to the bot."""
        try:
            self._setup_workspace(team_id, bot_token)
            # Start the handler for the new workspace
            self.handlers[team_id].start()
            logger.info(f"Added new workspace: {team_id}")
        except Exception as e:
            logger.error(f"Error adding workspace {team_id}: {e}")
            raise
