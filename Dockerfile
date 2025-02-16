# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    bash \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Ensure startup script has execute permissions
RUN chmod +x startup.sh && \
    mkdir -p /app/data && \
    chmod 777 /app/data

# Set environment variables
ENV DB_PATH=/app/data/messages.db \
    PORT=5000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose the web server port
EXPOSE 5000

# Health check using the /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Print environment variables and start the application
CMD ["/bin/bash", "-c", "env | sort && echo '=== Starting Application ===' && ./startup.sh"]
