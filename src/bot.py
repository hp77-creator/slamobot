import logging
from typing import List, Tuple
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


from .config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, GOOGLE_API_KEY
from .db import Database
from .llm import LLM

logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        self.app = App(token=SLACK_BOT_TOKEN)
        self.db = Database()
        self.model = LLM(API_KEY=GOOGLE_API_KEY, model_name='gemini-pro')
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up event handlers for the Slack bot."""
        @self.app.event("app_mention")
        def handle_mention(event, say):
            try:
                thread_ts = event.get("thread_ts", event["ts"])
                channel_id = event["channel"]
                user_message = event["text"]
                
                logger.info(f"Received mention: channel={channel_id}, thread={thread_ts}, "
                          f"message={user_message}")
                
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
                
                # TODO: Add LLM integration here
                response = self.model.get_chat_response(context) 
                logger.info(f"Sending response: {response}")
                
                # Store bot response
                self.db.store_message(channel_id, thread_ts, "BOT", response, True)
                
                # Send response
                say(blocks=format_response(response), thread_ts=thread_ts)
                
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
        """Start the Slack bot."""
        try:
            handler = SocketModeHandler(self.app, SLACK_APP_TOKEN)
            logger.info("Starting Slack bot...")
            handler.start()
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
