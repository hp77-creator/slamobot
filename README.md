# Slack Bot with LLM Integration

A Slack bot that uses Google's Gemini API to provide intelligent responses while maintaining conversation history.

## Features

- Responds to mentions in all contexts (channels, private channels, DMs, group messages)
- Maintains conversation history (last 5 messages)
- Includes both user messages and bot responses in context
- Uses Google's Gemini API for intelligent responses
- Supports multiple Slack workspaces
- Easy one-click installation
- Modular architecture for easy maintenance and extension

## Project Structure

```
slamobot/
├── src/
│   ├── __init__.py
│   ├── config.py      # Configuration settings
│   ├── db.py          # Database operations
│   ├── bot.py         # Slack bot implementation
│   └── web/           # Web server for OAuth
│       ├── __init__.py
│       ├── routes.py
│       └── templates/
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## Quick Setup

### Option 1: One-Click Installation (Recommended)

1. Visit our installation page: `https://your-bot-domain.up.railway.app`
2. Click "Add to Slack" button
3. Authorize the app for your workspace
4. Start using the bot in any channel or DM!

### Option 2: Local Development Setup

1. Create a Slack App:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Create New App > From scratch
   - Add necessary permissions:
     * app_mentions:read (respond to mentions)
     * chat:write (send messages)
     * channels:history (read public channels)
     * groups:history (read private channels)
     * im:history (read direct messages)
     * mpim:history (read group messages)
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
   SLACK_CLIENT_ID=your-client-id
   SLACK_CLIENT_SECRET=your-client-secret
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

   # Deploy with persistent volume for database
   railway up --volume /app/data
   ```

   Or deploy using GitHub:
   1. Fork this repository
   2. Create a new project in Railway
   3. Connect your GitHub repository
   4. Add environment variables in Railway dashboard:
      - SLACK_APP_TOKEN
      - SLACK_CLIENT_ID
      - SLACK_CLIENT_SECRET
      - GOOGLE_API_KEY
   5. Railway will automatically deploy on push

3. Interact with the bot:
   ```
   # In public channels
   /invite @YourBotName
   @YourBotName What's the weather like?

   # In private channels
   Add the bot to the channel first
   @YourBotName Hello!

   # In direct messages
   Just send a message to @YourBotName
   ```

## Development

- The bot uses SQLite for storing:
  * Message history (with thread context)
  * Workspace information (team ID, name, and tokens)
- Last 5 messages (including bot responses) are included in LLM context
- Supports multiple workspaces through OAuth installation
- Web server handles OAuth flow and provides installation page
- Works in all conversation contexts:
  * Public channels
  * Private channels
  * Direct messages
  * Group messages

## Production Deployment

1. Configure Slack App:
   - Add OAuth Redirect URL: `https://your-domain.up.railway.app/slack/oauth_redirect`
   - Set App Home URL: `https://your-domain.up.railway.app`
   - Enable public distribution if desired
   - Verify all scopes are properly configured

2. Set up Railway:
   - Configure environment variables
   - Set up persistent volume for database
   - Enable health checks
   - Configure custom domain (optional)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this code for your own projects.
