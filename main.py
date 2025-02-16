import argparse
import logging
import threading
import os

from src.bot import SlackBot
from src.web import app

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

    # Set up logging based on verbose flag
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Start the Slack bot in a separate thread
    bot_thread = threading.Thread(target=run_slack_bot)
    bot_thread.daemon = True  # Thread will exit when main program exits
    bot_thread.start()

    # Run the Flask web server in the main thread
    run_web_server(args.port)

if __name__ == "__main__":
    main()
