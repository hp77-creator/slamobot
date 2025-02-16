#!/bin/bash

echo "=== Current Environment ==="
env | sort

echo -e "\n=== Railway Variables ==="
env | grep "RAILWAY_" || echo "No Railway variables found"

echo -e "\n=== Required Variables Check ==="
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
  value="${!var}"
  if [ -z "$value" ]; then
    echo "❌ $var is not set"
    missing_vars+=("$var")
  else
    # Only show first 6 characters of sensitive values
    echo "✓ $var is set to: ${value:0:6}..."
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo -e "\n=== Troubleshooting Info ==="
  echo "Working Directory: $(pwd)"
  echo "Files in current directory:"
  ls -la
  
  echo -e "\nDocker Environment:"
  if [ -f /.dockerenv ]; then
    echo "Running inside Docker container"
  else
    echo "Not running in Docker container"
  fi
  
  echo -e "\nProcess Information:"
  ps aux | grep python || echo "No Python processes found"
  
  echo -e "\nError: Missing required environment variables: ${missing_vars[*]}"
  exit 1
fi

echo -e "\n=== All required environment variables are set ==="
echo "Starting application..."

# Start the application with verbose logging
exec python main.py --verbose
