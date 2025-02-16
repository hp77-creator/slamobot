#!/bin/bash

# Check required environment variables
required_vars=(
  "SLACK_BOT_TOKEN"
  "SLACK_APP_TOKEN"
  "SLACK_CLIENT_ID"
  "SLACK_CLIENT_SECRET"
  "GOOGLE_API_KEY"
)

# Print environment check header
echo "Checking environment variables..."

missing_vars=()
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ $var is not set"
    missing_vars+=("$var")
  else
    echo "✓ $var is set"
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: Missing required environment variables: ${missing_vars[*]}"
  exit 1
fi

echo "All required environment variables are set"
echo "Starting application..."

# Start the application with verbose logging
exec python main.py --verbose
