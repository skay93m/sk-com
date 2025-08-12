# Use official Python slim image
FROM python:3.11-slim

# Avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv directly
RUN apt-get update && apt-get install -y curl gcc \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && apt-get purge -y --auto-remove curl gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create and sync virtual environment using uv
RUN uv sync

# Activate virtual environment and collect static files
# Set a temporary secret key for collectstatic (not used in production)
ENV DJANGO_SECRET_KEY=temp-build-key-not-used-in-production
RUN uv run python manage.py collectstatic --noinput

# Start Gunicorn using the virtual environment
# Use shell form to allow environment variable expansion
CMD uv run gunicorn sk.wsgi:application --bind 0.0.0.0:${PORT:-8000}
