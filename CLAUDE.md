# CLAUDE.md — AI Assistant Guide for syafiqkay.com

## Project Overview

**Project Name:** syafiqkay.com (version 4.0.0)
**Purpose:** Personal index site for Syafiq Kay — content-first, identity-forward. Single place pointing to posts, LinkedIn, and future outputs.
**Live Site:** https://syafiqkay.com
**Type:** Django web application. No database for content — posts are markdown files in the repo.

## Technology Stack

### Backend
- **Python:** 3.13 (see `.python-version`)
- **Framework:** Django 6.x
- **WSGI Server:** Gunicorn
- **Database:** SQLite (local dev + production) — for Django auth/admin only, no app data
- **Package Manager:** UV

### Frontend
- **Template Engine:** Django Templates
- **CSS:** Bootstrap 5.3.3 via jsDelivr CDN (with SRI hash) + minimal inline styles in `base.html` for social icons and CV entry layout
- **No JavaScript, no local Bootstrap file**
- `static/style.css` exists but is empty — Bootstrap handles all layout and typography

### Key Dependencies
```
django>=5.2.4
markdown>=3.10.2
pyyaml (via commitizen)
gunicorn
whitenoise
python-dotenv
pytest
commitizen
```

## Directory Structure

```
sk-com/
├── manage.py
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── render.yaml
├── .python-version
├── syafiqkay/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                   # Single Django app
│   ├── views.py            # HomeView, WritingsView, PostDetailView, CVView, ContactView, RobotsTxtView
│   ├── urls.py             # App-level URL routing
│   ├── posts.py            # Markdown post loader utility
│   ├── apps.py
│   └── templates/
│       ├── base.html       # Base template (nav, footer, CSS link)
│       ├── index.html      # Homepage (bio + post list)
│       ├── writings.html   # Full post archive
│       ├── post.html       # Individual post
│       ├── cv.html         # CV page (placeholder)
│       └── contact.html    # Contact page (mailto link)
├── content/
│   └── posts/              # Markdown posts (.md files with YAML frontmatter)
├── static/
│   └── style.css           # All site CSS (~100 lines)
└── staticfiles/            # collectstatic output (gitignored)
```

## Post System

### Adding a Post

1. Create a `.md` file in `content/posts/`
2. Add YAML frontmatter at the top:

```markdown
---
title: Your Post Title
date: 2026-04-24
slug: your-post-slug
---

Post body in markdown.
```

1. Commit and push — Render auto-deploys.

### How Posts Are Served

- `core/posts.py` reads `.md` files once and caches them in memory — no build step needed
- `get_all_posts()` returns all valid posts sorted by date descending
- `get_post_by_slug(slug)` looks up from the same cache — no double parsing
- Missing `content/posts/` directory returns `[]`, never raises
- Individual post URLs: `/writings/<slug>/`

### Post Metadata Rules

- `title`, `date`, `slug`, `type` are all required — files missing any field are silently skipped
- `type` must be `blog` or `article` — any other value causes the file to be silently skipped
- `date` must be `YYYY-MM-DD` format; YAML date objects and ISO strings are both accepted and normalised to a `date` at parse time
- `slug` must contain only `[a-zA-Z0-9_-]` (Django's slug URL converter)
- Filename doesn't matter — slug in frontmatter is the canonical URL
- Posts are cached in memory after first load — restart the server to pick up new posts in development

## URL Structure

| Route | View | Purpose |
| --- | --- | --- |
| `/` | HomeView | Bio + post list |
| `/writings/` | WritingsView | Full post archive |
| `/writings/<slug>/` | PostDetailView | Individual post |
| `/cv/` | CVView | CV page |
| `/contact/` | ContactView | mailto link |
| `/admin/` | Django admin | Admin interface |
| `/robots.txt` | RobotsTxtView | Search robots |

## Views

All views are in `core/views.py`. All class-based (`TemplateView` or `View`).

- `HomeView` / `WritingsView` — pass `get_all_posts()` as context
- `PostDetailView` — calls `get_post_by_slug(slug)`, raises `Http404` if not found
- `CVView`, `ContactView` — bare TemplateView, no extra context
- `RobotsTxtView` — reads `robots.txt` from `BASE_DIR`, falls back to hardcoded default

## Development Workflows

### Initial Setup

```bash
uv sync
export DJANGO_SECRET_KEY="your-secret-key-here"
export DEBUG="True"
export ALLOWED_HOSTS="localhost,127.0.0.1"
uv run python manage.py migrate
uv run python manage.py runserver
```

### Common Commands

```bash
uv run python manage.py runserver        # Dev server
uv run python manage.py migrate          # Apply migrations (SQLite only)
uv run python manage.py collectstatic    # Collect static files
uv run pytest                            # Run tests
uv run python manage.py createsuperuser  # Create admin user
```

## Settings (`syafiqkay/settings.py`)

Key settings:

- `DATABASES` — SQLite only (`db.sqlite3`, gitignored)
- `CONTENT_DIR` — `BASE_DIR / 'content'` — used by `core/posts.py`
- `STATICFILES_DIRS` — `[BASE_DIR / 'static']` — source CSS files
- `STATIC_ROOT` — `staticfiles/` — collectstatic output (gitignored)
- All security settings preserved (HSTS, HTTPS redirect, secure cookies)

## Deployment

### Platform

- **Host:** Render.com
- **Config:** `render.yaml`
- **Database:** SQLite (ephemeral per deploy — admin users reset on redeploy)
- **Domains:** [sk-website.onrender.com](https://sk-website.onrender.com), [syafiqkay.com](https://syafiqkay.com), [www.syafiqkay.com](https://www.syafiqkay.com)

### Build Process
1. `pip install uv && uv sync`
2. `uv run python manage.py migrate`
3. `uv run python manage.py collectstatic --noinput`

### Start Command
```bash
uv run gunicorn syafiqkay.wsgi:application --bind 0.0.0.0:$PORT
```

## Code Conventions

### Core Principles

- **DRY** — single source of truth, no repeated logic
- **Clean Code** — readable, small functions, meaningful names
- **Minimal by design** — do not add complexity that isn't needed

### Styling

- Bootstrap 5.3.3 CDN — use Bootstrap utility classes in templates
- Minimal inline `<style>` block in `base.html` for social icon colours/sizes and CV entry layout
- `static/style.css` is intentionally empty — do not add custom CSS

### File Naming
- Python files: lowercase with underscores
- Templates: lowercase with underscores

## Important Notes for AI Assistants

### Critical Do's
1. **Read files before editing**
2. **Use `uv run` for all Python commands**
3. **Use lowercase template names**
4. **Commit `static/style.css`** — `.gitignore` only ignores `staticfiles/` not `static/`
5. **Frontmatter required** — posts without `title`, `date`, `slug` are silently skipped

### Critical Don'ts

1. **Don't add a database** — SQLite is only for auth/admin, never for content
2. **Don't add Bootstrap or external CSS/JS**
3. **Don't add models** — content lives in markdown files
4. **Don't hardcode secrets**
5. **Don't use pip directly** — use UV

### When Making Changes

1. **Adding a post:** create `.md` file in `content/posts/` with frontmatter
2. **Changing site design:** edit `static/style.css` only
3. **Changing layout structure:** edit `core/templates/base.html`
4. **Adding a new page/route:** add view in `core/views.py`, URL in `core/urls.py`, template in `core/templates/`
5. **Changing post rendering:** edit `core/posts.py` (`_parse_post_file`)

## Environment Variables

### Required

- `DJANGO_SECRET_KEY`

### Optional with Defaults

- `DEBUG` (default: "False")
- `ALLOWED_HOSTS` (default: "")

### Production (set in render.yaml)

- `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `WHITENOISE_USE_FINDERS`, `WHITENOISE_AUTOREFRESH`

## Git Workflow

Simplified Git Flow — same as before:

- `main` — production-ready
- `feature/*` — new features
- `hotfix/*` — urgent fixes
- `claude/*` — AI assistant work

### Conventional Commits
Format: `<type>: <description>`
Types: feat, fix, docs, style, refactor, test, chore

---

**Last Updated:** 2026-04-24
**Architecture:** Django + Markdown files, no content DB
**Python Version:** 3.13
**Django Version:** 6.x
