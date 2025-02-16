import sqlite3
from datetime import datetime
import logging
from typing import List, Tuple, Optional

from .config import DB_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """Initialize the database and create necessary tables."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                
                # Create workspaces table first
                c.execute('''
                    CREATE TABLE IF NOT EXISTS workspaces
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT UNIQUE,
                    team_name TEXT,
                    bot_token TEXT,
                    bot_id TEXT,
                    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                ''')
                
                # Check if bot_id column exists
                c.execute("PRAGMA table_info(workspaces)")
                columns = [col[1] for col in c.fetchall()]
                if 'bot_id' not in columns:
                    logger.info("Adding bot_id column to workspaces table")
                    c.execute('ALTER TABLE workspaces ADD COLUMN bot_id TEXT')
                
                # Create messages table
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
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_workspaces(self) -> List[Tuple[str, str, str, str]]:
        """Get all workspaces from the database."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                c.execute('SELECT team_id, team_name, bot_token, bot_id FROM workspaces')
                return c.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting workspaces: {e}")
            return []

    def get_workspace(self, team_id: str) -> Optional[Dict[str, str]]:
        """Get a specific workspace's details."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    SELECT team_id, team_name, bot_token, bot_id 
                    FROM workspaces 
                    WHERE team_id = ?
                ''', (team_id,))
                result = c.fetchone()
                if result:
                    return {
                        "team_id": result[0],
                        "team_name": result[1],
                        "bot_token": result[2],
                        "bot_id": result[3]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Error getting workspace {team_id}: {e}")
            return None

    def add_workspace(self, team_id: str, team_name: str, bot_token: str, bot_id: str) -> bool:
        """Add or update a workspace in the database."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                # Update schema if needed
                c.execute('''
                    CREATE TABLE IF NOT EXISTS workspaces
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id TEXT UNIQUE,
                    team_name TEXT,
                    bot_token TEXT,
                    bot_id TEXT,
                    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                ''')
                
                # Insert or update workspace
                c.execute('''
                    INSERT OR REPLACE INTO workspaces 
                    (team_id, team_name, bot_token, bot_id)
                    VALUES (?, ?, ?, ?)
                ''', (team_id, team_name, bot_token, bot_id))
                conn.commit()
            logger.info(f"Workspace added/updated: {team_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding workspace: {e}")
            return False

    def store_message(self, channel_id: str, thread_ts: str, user_id: str, 
                     message: str, is_bot: bool) -> None:
        """Store a message in the database."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                is_bot_str = 'true' if is_bot else 'false'
                c.execute('''
                INSERT INTO messages (channel, thread_ts, user_id, message, is_bot, timestamp)
                VALUES(?, ?, ?, ?, ?, ?)
                ''', (channel_id, thread_ts, user_id, message, is_bot_str, 
                     datetime.now().isoformat()))
                conn.commit()
            logger.info(f"Stored message: channel={channel_id}, thread={thread_ts}, "
                       f"user={user_id}, is_bot={is_bot_str}")
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            raise

    def get_thread_history(self, channel_id: str, thread_ts: str, 
                          limit: int = 5) -> List[Tuple[str, str]]:
        """Retrieve message history for a thread."""
        try:
            with self.get_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    SELECT message, is_bot FROM messages 
                    WHERE channel=? AND thread_ts=?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (channel_id, thread_ts, limit))
                messages = c.fetchall()
            logger.info(f"Retrieved {len(messages)} messages for thread {thread_ts}")
            return messages[::-1]  # Reverse to get chronological order
        except Exception as e:
            logger.error(f"Error retrieving thread history: {e}")
            return []
