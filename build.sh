#!/bin/bash
set -e

# Install dependencies
uv sync

# Run migrations
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --noinput
