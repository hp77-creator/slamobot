import os
import argparse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import logging

# Set up argument parser
parser = argparse.ArgumentParser(description='Slack Bot with optional verbose logging')
parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
args = parser.parse_args()

# Set up logging based on verbose flag
if args.verbose:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def init_db():
    try:
        conn = sqlite3.connect('messages.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            thread_ts TEXT,
            user_id TEXT,
            message TEXT,
            is_bot TEXT,
            timestamp TEXT)
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

def get_thread_history(channel_id, thread_ts):
    try:
        conn = sqlite3.connect('messages.db')
        c = conn.cursor()
        c.execute('''
            SELECT message, is_bot FROM messages 
            WHERE channel=? AND thread_ts=?
            ORDER BY timestamp DESC LIMIT 5
        ''', (channel_id, thread_ts))
        messages = c.fetchall()
        conn.close()
        logger.info(f"Retrieved {len(messages)} messages for thread {thread_ts}")
        return messages[::-1]
    except Exception as e:
        logger.error(f"Error retrieving thread history: {e}")
        return []


def store_message(channel_id, thread_ts, user_id, message, is_bot):
    try:
        conn = sqlite3.connect('messages.db')
        c = conn.cursor()
        # Convert boolean is_bot to string 'true' or 'false'
        is_bot_str = 'true' if is_bot else 'false'
        c.execute('''
        INSERT INTO messages (channel, thread_ts, user_id, message, is_bot, timestamp)
        VALUES(?, ?, ?, ?, ?, ?)
        ''', (channel_id, thread_ts, user_id, message, is_bot_str, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"Stored message: channel={channel_id}, thread={thread_ts}, user={user_id}, is_bot={is_bot_str}")
    except Exception as e:
        logger.error(f"Error storing message: {e}")

@app.event("app_mention")
def handle_mention(event, say):
    try:
        thread_ts = event.get("thread_ts", event["ts"])
        channel_id = event["channel"]
        user_message = event["text"]
        
        logger.info(f"Received mention: channel={channel_id}, thread={thread_ts}, message={user_message}")
        
        # Store user message
        store_message(channel_id, thread_ts, event["user"], user_message, False)
        
        # Get conversation history
        history = get_thread_history(channel_id, thread_ts)
        logger.info(f"Retrieved history: {history}")
        
        # Convert 'true'/'false' strings back to boolean for formatting
        context = "\n".join([
            f"{'Bot' if is_bot == 'true' else 'User'}: {msg}" 
            for msg, is_bot in history
        ])
        
        response = f"I received your message. History:\n{context}"
        logger.info(f"Sending response: {response}")
        
        # Store bot response
        store_message(channel_id, thread_ts, "BOT", response, True)
        
        # Send response
        say(text=response, thread_ts=thread_ts)
        
    except Exception as e:
        logger.error(f"Error in handle_mention: {e}")
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        say(text=error_msg, thread_ts=thread_ts)



init_db()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
