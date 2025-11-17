# ESP32 Weather Station Dashboard - Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (no MySQL needed for Firebase)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with retry logic
RUN pip install --no-cache-dir --retries 3 --timeout 300 -r requirements.txt

# Copy application files
COPY python_mqtt_subscriber.py .
COPY app.py .

# Create templates directory and copy dashboard
RUN mkdir -p templates
COPY templates/dashboard.html templates/

# Install supervisord for running multiple processes
RUN pip install supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisord.conf

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port for Flask application
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start supervisord to run both MQTT subscriber and Flask app
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]