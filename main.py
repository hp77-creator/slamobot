import argparse
import logging
import threading
import os
import sys

from src.bot import SlackBot
from src.web import app
from src import config

def setup_logging(verbose: bool) -> None:
    """Configure logging with proper format and level."""
    log_level = logging.INFO if verbose else logging.WARNING
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout  # Ensure logs go to stdout for Railway
    )
    
    # Set Flask's logger to the same level
    logging.getLogger('werkzeug').setLevel(log_level)

def run_slack_bot():
    """Run the Slack bot in a separate thread."""
    try:
        bot = SlackBot()
        bot.start()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        raise

def run_web_server(port):
    """Run the Flask web server."""
    try:
        # Log the port we're using
        logging.info(f"Starting web server on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logging.error(f"Failed to start web server: {e}")
        raise

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Slack Bot with web interface')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)),
                      help='Port for the web server')
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Log startup information
    logging.info("Starting Slamobot...")
    logging.info(f"Environment: SLACK_CLIENT_ID={'Yes' if config.SLACK_CLIENT_ID else 'No'}")
    logging.info(f"Environment: SLACK_CLIENT_SECRET={'Yes' if config.SLACK_CLIENT_SECRET else 'No'}")
    logging.info(f"Environment: SLACK_APP_TOKEN={'Yes' if config.SLACK_APP_TOKEN else 'No'}")
    logging.info(f"Environment: GOOGLE_API_KEY={'Yes' if config.GOOGLE_API_KEY else 'No'}")

    # Start the Slack bot in a separate thread
    bot_thread = threading.Thread(target=run_slack_bot)
    bot_thread.daemon = True  # Thread will exit when main program exits
    bot_thread.start()

    # Run the Flask web server in the main thread
    run_web_server(args.port)

if __name__ == "__main__":
    main()
