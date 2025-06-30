FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose the port (configurable via environment)
EXPOSE 8000

# Command to run the application with environment variables
CMD uvicorn src.main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --reload=${AUTO_RELOAD:-false}