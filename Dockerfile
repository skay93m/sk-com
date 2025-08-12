# Use official Python slim image
FROM python:3.11-slim

# Avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv directly
# Define build dependencies for easier future maintenance
ARG BUILD_DEPS="curl gcc"

RUN apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && apt-get purge -y --auto-remove $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first to leverage Docker cache
COPY requirements.txt ./

# Copy project files
COPY . .

# Create and sync virtual environment using uv
RUN uv sync

# Start Gunicorn using the virtual environment
# Use shell form to allow environment variable expansion
# Update 'sk.wsgi:application' to match your actual project structure, e.g. 'myproject.wsgi:application'
CMD uv run gunicorn myproject.wsgi:application --bind 0.0.0.0
# Start Gunicorn using the virtual environment
# Use shell form to allow environment variable expansion
CMD uv run gunicorn sk.wsgi:application --bind 0.0.0.0
