# Use official Python slim image
FROM python:3.11-slim

# Avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv via pipx
RUN apt-get update && apt-get install -y curl gcc \
    && pip install pipx \
    && pipx ensurepath \
    && pipx install uv \
    && apt-get purge -y --auto-remove curl gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create and sync virtual environment using uv
RUN uv venv .venv && \
    .venv/bin/uv pip sync uv.lock

# Activate virtual environment and collect static files
RUN .venv/bin/python manage.py collectstatic --noinput

# Start Gunicorn using the virtual environment
CMD [".venv/bin/gunicorn", "sk.wsgi:application", "--bind", "0.0.0.0:$PORT"]
