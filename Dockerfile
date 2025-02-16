# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for SQLite database with proper permissions
# Note: For production, consider mounting this directory as a volume
# railway up --volume /app/data
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Set environment variables
ENV DB_PATH=/app/data/messages.db
ENV PORT=5000

# Expose the web server port
EXPOSE 5000

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Run the bot
CMD ["python", "main.py"]
