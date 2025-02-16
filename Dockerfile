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

# Copy the entire application
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure startup script has execute permissions
RUN chmod +x startup.sh && \
    mkdir -p /app/data && \
    chmod 777 /app/data

# Set environment variables
ENV DB_PATH=/app/data/messages.db \
    PORT=5000 \
    PYTHONUNBUFFERED=1

# Expose the web server port
EXPOSE 5000

# Run the startup script
CMD ["./startup.sh"]
