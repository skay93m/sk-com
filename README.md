# sk-com

Source for [syafiqkay.com](https://syafiqkay.com), the personal site of Syafiq Kay.

A small Django application with no application database. Posts and lab write-ups are
markdown files in `content/`, parsed and cached in memory at first request. Deployed as
a Docker web service on Render.

## Stack

Django 6 on Python 3.13, managed with [uv](https://docs.astral.sh/uv/). Gunicorn and
WhiteNoise in production. Django templates and plain CSS, with no framework and no
build step.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Bio, positioning and recent posts |
| `/writings/`, `/writings/<slug>/` | Posts and essays |
| `/labs/`, `/labs/<slug>/` | Technical lab write-ups, grouped by project |
| `/cv/` | CV |

## Running locally

```bash
uv sync
export DJANGO_SECRET_KEY="anything-for-local-use"
export DEBUG="True"
export ALLOWED_HOSTS="localhost,127.0.0.1"
uv run python manage.py migrate
uv run python manage.py runserver
uv run pytest
```

Posts are cached after first load, so restart the server to pick up new markdown files.

## Contributing

This is a personal site and is not open to outside contributions. Content is governed by
a deny-by-default publication policy, and interactive tools are required to be
client-side only. Both are documented in [CLAUDE.md](CLAUDE.md), with security posture
in [SECURITY.md](SECURITY.md).

Never push directly to `main`. Render deploys on every commit to it.
