# Slack Bot with LLM Integration

A Slack bot that uses Google's Gemini API to provide intelligent responses while maintaining conversation history.

## Features

- Responds to mentions in Slack channels
- Maintains conversation history (last 5 messages)
- Includes both user messages and bot responses in context
- Uses Google's Gemini API for intelligent responses
- Modular architecture for easy maintenance and extension

## Project Structure

```
slamobot/
├── src/
│   ├── __init__.py
│   ├── config.py      # Configuration settings
│   ├── db.py          # Database operations
│   └── bot.py         # Slack bot implementation
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## Local Setup

1. Create a Slack App:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Create New App > From scratch
   - Add necessary permissions:
     * app_mentions:read
     * chat:write
     * channels:history
   - Enable Socket Mode
   - Install to workspace
   - Copy Bot User OAuth Token and App-Level Token

2. Set up environment:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd slamobot

   # Create virtual environment and install dependencies using uv
   uv venv
   uv pip install -r requirements.txt
   
   # Activate virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Configure environment variables:
   ```bash
   # Create .env file
   cp .env.example .env

   # Edit .env with your tokens
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token
   GOOGLE_API_KEY=your-gemini-api-key
   ```

## Usage

1. Start the bot locally:
   ```bash
   # Run without verbose logging
   python main.py

   # Run with verbose logging
   python main.py --verbose
   ```

2. Deploy to Railway (Recommended for production):
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli

   # Login to Railway
   railway login

   # Create a new project
   railway init

   # Deploy the project
   railway up
   ```

   Or deploy using GitHub:
   1. Fork this repository
   2. Create a new project in Railway
   3. Connect your GitHub repository
   4. Add environment variables in Railway dashboard:
      - SLACK_BOT_TOKEN
      - SLACK_APP_TOKEN
      - GOOGLE_API_KEY
   5. Railway will automatically deploy on push

3. Invite the bot to a channel:
   ```
   /invite @YourBotName
   ```

3. Mention the bot to get a response:
   ```
   @YourBotName What's the weather like?
   ```

## Development

- The bot uses SQLite for storing message history (persistent in Railway deployment)
- Messages are stored with thread context
- Last 5 messages (including bot responses) are included in LLM context

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this code for your own projects.
