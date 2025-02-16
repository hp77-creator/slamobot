import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime 

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def init_db():
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

def get_thread_history(channel_id, thread_ts):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''
        SELECT message, is_bot FROM messages 
        WHERE channel=? AND thread_ts=?
        ORDER BY timestamp DESC LIMIT 5
    ''', (channel_id, thread_ts))
    messages = c.fetchall()
    conn.close()
    return messages[::-1]


def store_message(channel_id, thread_ts, user_id, message, is_bot):
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO messages (channel, thread_ts, user_id, message, is_bot, timestamp)
    VALUES(?, ?, ?, ?, ?, ?)
    ''', (channel_id, thread_ts, user_id, message, is_bot, datetime.now().isoformat())
    )

@app.event("app_mention")
def handle_mention(event, say):
    thread_ts = event.get("thread_ts", event["ts"])
    channel_id = event["channel"]
    user_message = event["text"]

    store_message(channel_id, thread_ts, event["user"], user_message, False)

    history = get_thread_history(channel_id, thread_ts)

    context = "\n".join([
        f"{'Bot' if is_bot else 'User'}: {msg}" 
        for msg, is_bot in history
    ])

    try:
        response = f"I received your message. History:\n{context}"

        store_message(channel_id, thread_ts, "BOT", response, True)
        say(text=response, thread_ts=thread_ts)
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        say(text=error_msg, thread_ts=thread_ts)



init_db()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()