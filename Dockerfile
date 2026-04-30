FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend only
COPY backend backend/

# Create necessary directories (will be empty on first run)
RUN mkdir -p uploads db

# Expose port
EXPOSE 8000

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_DEBUG=false
ENV PORT=8000

# Run application with gunicorn
CMD exec gunicorn --workers 2 --worker-class sync --timeout 120 --bind 0.0.0.0:$PORT backend.app:app
