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
pytest-django
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
│   ├── views.py            # HomeView, WritingsView, PostDetailView, CVView, LabsView, LabDetailView, RobotsTxtView
│   ├── urls.py             # App-level URL routing
│   ├── posts.py            # Markdown post loader utility
│   ├── apps.py
│   └── templates/
│       ├── base.html       # Base template (nav, footer, Bootstrap CDN)
│       ├── index.html      # Homepage (bio + post list + social links)
│       ├── writings.html   # Full post archive
│       ├── post.html       # Individual post
│       ├── cv.html         # CV page
│       ├── labs.html       # Lab listing
│       └── lab.html        # Individual lab
├── content/
│   ├── posts/              # Markdown posts (.md files with YAML frontmatter)
│   └── labs/               # Markdown lab write-ups (Network+, tools, experiments)
├── static/
│   ├── style.css           # Intentionally empty — Bootstrap 5.3.3 CDN handles all styling
│   └── labs/               # Lab topology images and downloadable assets (e.g. .pkt files)
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
type: blog
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
- `type` must be `blog` or `article` — any other value causes the file to be silently skipped (labs use `type: lab` and live in `content/labs/`, not `content/posts/`)
- `date` must be `YYYY-MM-DD` format; YAML date objects and ISO strings are both accepted and normalised to a `date` at parse time
- `slug` must contain only `[a-zA-Z0-9_-]` (Django's slug URL converter)
- Filename doesn't matter — slug in frontmatter is the canonical URL
- Posts are cached in memory after first load — restart the server to pick up new posts in development

## URL Structure

| Route | View | Purpose |
| --- | --- | --- |
| `/` | HomeView | Bio + post list + social links |
| `/writings/` | WritingsView | Full post archive |
| `/writings/<slug>/` | PostDetailView | Individual post |
| `/cv/` | CVView | CV page |
| `/labs/` | LabsView | Lab write-up listing |
| `/labs/<slug>/` | LabDetailView | Individual lab |
| `/admin/` | Django admin | Admin interface |
| `/robots.txt` | RobotsTxtView | Search robots |

## Views

All views are in `core/views.py`. All class-based (`TemplateView` or `View`).

- `HomeView` / `WritingsView` — pass `get_all_posts()` as context
- `PostDetailView` — calls `get_post_by_slug(slug)`, raises `Http404` if not found
- `LabsView` — passes `get_all_labs()` as context
- `LabDetailView` — calls `get_lab_by_slug(slug)`, raises `Http404` if not found
- `CVView` — bare TemplateView, no extra context
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

1. **Adding a post:** create `.md` file in `content/posts/` with frontmatter (`title`, `date`, `slug`, `type: blog|article`)
2. **Adding a lab:** create `.md` file in `content/labs/` with frontmatter (`title`, `date`, `slug`, `type: lab`) — optional: `tools`, `objectives`, `skills`
3. **Changing layout structure:** edit `core/templates/base.html`
4. **Adding a new page/route:** add view in `core/views.py`, URL in `core/urls.py`, template in `core/templates/`
5. **Changing post/lab rendering:** edit `core/posts.py` (`_parse_post_file`) or `core/labs.py` (`_parse_lab_file`)

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

Simplified Git Flow:

- `main` — production-ready; **Render deploys immediately on every push to main**
- `feature/*` — new features
- `hotfix/*` — urgent fixes
- `claude/*` — AI assistant work
- `post/<slug>` — individual blog post or article (used by `/publish` command)
- `lab/<slug>` — individual lab write-up (used by `/publish` command)

### CRITICAL: Never push directly to main

Every change to main must go through a GitHub pull request — no exceptions.
Pushing directly to main triggers an immediate production deploy with no review gate.

**Correct workflow:**

1. Work on a feature branch
2. `git push -u origin feature/<name>`
3. Create a PR on GitHub (`gh pr create` or via web)
4. Review the diff on GitHub before merging
5. Merge via GitHub web UI — this is what triggers the Render deploy
6. Locally: `git checkout main && git pull` to sync
7. Branch next feature from the updated main: `git checkout -b feature/<next> origin/main`

**If main advances while your PR branch is behind:** GitHub shows an "Update branch"
button on the PR — click it to merge latest main in. Locally: `git merge origin/main`
or `git rebase origin/main` on your feature branch. This is normal; feature branches
diverge and get reconciled at merge time.

### Conventional Commits
Format: `<type>: <description>`
Types: feat, fix, docs, style, refactor, test, chore

---

**Last Updated:** 2026-05-16
**Architecture:** Django + Markdown files, no content DB
**Python Version:** 3.13
**Django Version:** 6.x
