#!/bin/bash

# Build script for Render deployment
set -e

echo "Starting build process..."

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
uv sync

# Collect static files
echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Build completed successfully!"
