import argparse
import logging

from src.bot import SlackBot

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Slack Bot with optional verbose logging')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    # Set up logging based on verbose flag
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize and start the bot
    try:
        bot = SlackBot()
        bot.start()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
