# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for SQLite database with proper permissions
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Set environment variable for database path
ENV DB_PATH=/app/data/messages.db

# Run the bot
CMD ["python", "main.py"]
