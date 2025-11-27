FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG BUILD_DEPS="curl gcc"

RUN apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && apt-get purge -y --auto-remove $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# Collect static files during build
RUN uv run python manage.py collectstatic --noinput

CMD uv run gunicorn sk.wsgi:application --bind 0.0.0.0:${PORT:-8000}
