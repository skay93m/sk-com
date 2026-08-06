# CLAUDE.md — AI Assistant Guide for syafiqkay.com

## Project Overview

**Project Name:** syafiqkay.com
**Purpose:** Personal site for Syafiq Kay. Content-first and identity-forward, positioned on the braided intersection of clinical practice, law and technical work. It exists to make that combination legible and to host evidence of ongoing work, not to serve as a brochure. Governing intent lives in `pm/Website Redesign` in the Musubi vault; this file governs implementation.
**Live Site:** [https://syafiqkay.com](https://syafiqkay.com)
**Type:** Django web application. No database for content — posts are markdown files in the repo.

## Technology Stack

### Backend

- **Python:** 3.13 (see `.python-version`)
- **Framework:** Django 6.x
- **WSGI Server:** Gunicorn
- **Database:** SQLite, Django auth and admin only, no app data. Scheduled for removal along with the admin, since the app defines no models
- **Package Manager:** UV

### Frontend

- **Template Engine:** Django Templates
- **CSS:** one hand-written stylesheet at `static/style.css`. No CSS framework, no CDN, no npm, no build step
- **JavaScript:** none site-wide. Vanilla JS only inside a `/tools/` page that needs it, never a framework
- **Current state:** Bootstrap 5.3.3 via CDN is still wired into `base.html` and `static/style.css` is still empty. Removing Bootstrap and writing the stylesheet is Phase 1 of the redesign and has not happened yet. Do not add new Bootstrap usage in the meantime

### Key Dependencies

```text
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
│   ├── style.css           # The site's only stylesheet (currently still empty, see Phase 1)
│   └── labs/               # Lab topology images and downloadable assets (e.g. .pkt files)
└── staticfiles/            # collectstatic output (gitignored)
```

## Content System

### Publishing new content

Use the `/publish` command — pass a file path or paste the markdown directly. It validates frontmatter, creates the correct branch (`post/<slug>` or `lab/<slug>`), writes the file, commits, and pushes. You then review and merge the PR yourself.

```text
/publish path/to/draft.md
```

See `.claude/commands/publish.md` for full field rules and validation behaviour.

### Editing existing content

Open the `.md` file in `content/posts/` or `content/labs/`, make your edits, then commit on a feature branch and open a PR. **Do not change the `slug`** — it is the URL and changing it breaks existing links.

### CV updates

The CV is a Django template, not a markdown file. Edit `core/templates/cv.html` directly. For the bio paragraph (shown on homepage and CV), edit `core/context_processors.py`.

### How Posts Are Served

- `core/posts.py` reads `.md` files once and caches them in memory — no build step needed
- `get_all_posts()` returns all valid posts sorted by date descending
- `get_post_by_slug(slug)` looks up from the same cache — no double parsing
- Missing `content/posts/` directory returns `[]`, never raises
- Individual post URLs: `/writings/<slug>/`

### Post Metadata Rules

- `title`, `date`, `slug`, `type`, `author` are all required — files missing any field are silently skipped
- `author` must be `Syafiq Kay` — used in `<meta name="author">` and `<meta name="citation_author">` for citation tools
- `type` must be `blog` or `article` — any other value causes the file to be silently skipped (labs use `type: lab` and live in `content/labs/`, not `content/posts/`)
- `date` must be `YYYY-MM-DD` format; YAML date objects and ISO strings are both accepted and normalised to a `date` at parse time
- `slug` must contain only `[a-zA-Z0-9_-]` (Django's slug URL converter)
- Filename doesn't matter — slug in frontmatter is the canonical URL
- Posts are cached in memory after first load — restart the server to pick up new posts in development

### How Labs Are Served

- `core/labs.py` reads `.md` files from `content/labs/` and caches them in memory
- `get_labs_grouped_by_project()` groups labs by their `project` slug, sorted by most recent lab per project
- Project metadata (name, description) comes from `content/labs/projects.yaml`
- Labs whose `project` slug is not in `projects.yaml` are excluded from `/labs/` — they are silently skipped at grouping time
- Individual lab URLs: `/labs/<slug>/`

### Lab Metadata Rules

- `title`, `date`, `slug`, `type`, `project`, `author` are all required — any missing field silently skips the file
- `author` must be `Syafiq Kay` — used in `<meta name="author">` and `<meta name="citation_author">` for citation tools
- `type` must be exactly `lab`
- `project` must match a slug defined in `content/labs/projects.yaml` — see that file for the current list
- `tools`, `objectives`, `skills` are optional lists; `skills` values appear as badges on `/labs/`
- **Do not change `slug` after publishing** — it is the URL

### Lab frontmatter example

```markdown
---
title: VLAN Segmentation on a Cisco Switch
date: 2026-05-16
slug: vlan-segmentation-cisco
type: lab
project: comptia-network-plus
author: Syafiq Kay
tools:
  - Cisco Packet Tracer
  - Cisco IOS CLI
objectives:
  - Configure VLANs 10, 20, 30 on a 2960 switch
skills:
  - VLANs
  - Cisco IOS
---
```

### Lab static assets

Topology images and downloadable files (e.g. `.pkt`) live in `static/labs/<slug>/`.
Reference them in the lab body as `/static/labs/<slug>/topology.png`. Create the folder
manually alongside the lab file — the `/publish` command does not create it.

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
- `LabsView` — passes `get_labs_grouped_by_project()` as `projects` context
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

- **Host:** Render.com, Frankfurt region
- **Service:** web service named `syafiqkay.com` (`srv-d1jhn92li9vc73894ek0`), **Docker runtime**, starter plan, auto-deploys on push to `main`, pull request previews enabled
- **Build and run:** entirely from `Dockerfile`. There is no Render build or start command
- **Config:** `render.yaml` is **not** synced as a Blueprint. The dashboard is authoritative. Editing `render.yaml` does not change the running service
- **Database:** SQLite at `BASE_DIR / db.sqlite3`, Django auth and admin only. Ephemeral, since it is inside the container and not on the mounted disk
- **Domains:** [syafiqkay.com](https://syafiqkay.com), [www.syafiqkay.com](https://www.syafiqkay.com), and the Render URL [syafiq-kay-1.onrender.com](https://syafiq-kay-1.onrender.com). The former Render URL `sk-website.onrender.com` is also kept in `ALLOWED_HOSTS`
- **Note:** `settings.py` line 29 appends `.onrender.com` to `ALLOWED_HOSTS` unconditionally, so every `.onrender.com` host is accepted whether listed or not. The explicit entries are documentation rather than access control

### Known deployment drift

Recorded 2026-08-06, not yet resolved. Do not assume these are fixed.

- A **Render PostgreSQL instance is provisioned and billed** and its `DATABASE_URL` is set on the service, but `settings.py` hardcodes SQLite and never reads it. It is connected to nothing
- A **1 GB persistent disk is mounted at `/ssd`** and nothing writes to it. It also prevents zero-downtime deploys
- `DJANGO_SECRET_KEY` on the live service is a `django-insecure-` development key, not a generated one
- A **`GITHUB_TOKEN` personal access token is set on the web service** and no application code reads it

### Build Process

Defined in `Dockerfile`. `collectstatic` runs at image build time. There is no `migrate` step in the image.

## Publication Policy

Mirrored from `areas/Website` in the Musubi vault, which is the authoritative copy.
**Deny by default.** Content clears every rule below or it does not go on the site.

1. **Nothing about Boots as an employer.** No grievance material, no workplace disputes, no colleagues, no internal process.
2. **No patient cases, including anonymised ones.** Clinical writing operates at the level of published evidence, guidance and law, never practice anecdote.
3. **No finances.**
4. **Pharmacy appears as expertise and analysis**, never as reportage of working life.
5. **Tools receive no user data at the server.** See below.
6. **Vault-derived content reaches the site only through a reviewed pull request diff**, never a live query from the running app.

If you are unsure whether something clears these, stop and ask. Do not publish and await correction.

### Tools are client-side only

`/tools/` pages exist to be used on a hotdesking work computer, which means clinical
detail will be typed into them. If any of that reaches the server it creates a patient
data flow into a personal website with no lawful basis, no retention policy and no
controller relationship.

- Server sends HTML, CSS and vanilla JavaScript. All computation happens in the browser
- No form POST, no `fetch`, no XHR, no WebSocket back to the origin
- No analytics, no cookies, no `localStorage` or `sessionStorage` for anything clinical
- No login. A tool that holds no data needs no gate, and typing credentials on a shared machine is its own risk
- Every tool page carries a visible statement that nothing entered leaves the device and nothing is stored
- Every tool page has a clear button and print-friendly styling

This is an architectural constraint, not a preference. A tool that posts to the server is wrong even if it works.

## Code Conventions

### Core Principles

- **DRY** — single source of truth, no repeated logic
- **Clean Code** — readable, small functions, meaningful names
- **Minimal by design** — do not add complexity that isn't needed

### Styling

- All styling lives in `static/style.css`. Write plain CSS there
- Target aesthetic: sharp academic notebook. Minimal single-column layout, serif-ish type, identity-forward and content-first
- No CSS framework, no CDN, no inline `<style>` blocks in templates
- Print styles matter for `/tools/` pages, since work output often ends up on paper

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

1. **Don't add a database** — content lives in markdown files. The remaining SQLite config serves only Django auth/admin and is scheduled for removal
2. **Don't add a CSS or JS framework, a CDN, or an npm build step** — plain CSS in `static/style.css`, vanilla JS only where a tool needs it
3. **Don't add models** — content lives in markdown files
4. **Don't hardcode secrets**
5. **Don't use pip directly** — use UV

### When Making Changes

1. **Adding a post or lab:** use the `/publish` command — pass a file path or paste the markdown content directly:

   ```text
   /publish <path-to-draft.md>
   ```

   or

   ```text
   /publish
   ---
   title: My Post
   ...
   ---
   Body here.
   ```

   The command validates frontmatter, creates the correct branch, writes the file, and pushes. See `.claude/commands/publish.md` for full rules.
2. **Editing an existing post or lab:** edit the `.md` file directly, commit on a feature branch, open a PR. Do not change the `slug`.
3. **Updating the CV:** edit `core/templates/cv.html`; for the bio paragraph edit `core/context_processors.py`
4. **Changing layout structure:** edit `core/templates/base.html`
5. **Adding a new page/route:** add view in `core/views.py`, URL in `core/urls.py`, template in `core/templates/`
6. **Changing post/lab rendering:** edit `core/posts.py` (`_parse_post_file`) or `core/labs.py` (`_parse_lab_file`)
7. **Adding a new project category for labs:** add an entry to `content/labs/projects.yaml`

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

## Future Work (Backlog)

These are planned features. Do not implement unless explicitly asked.

- **CV content from file** — refactor `cv.html` so each section is driven by `content/config/cv.yaml` rather than hardcoded HTML
- **Bio from file** — `content/config/bio.yaml` replaces hardcoded bio in `core/context_processors.py`
- **Dedicated project page** — `/labs/project/<slug>/` with full project description and all its labs
- **Pagination** — for the writings list once it grows long enough; feature branch `feature/pagination`
- **Projects page** — `/projects/` as a lab notebook: each experiment with aim, hypothesis, method, and running observations. Distinct from CV; feature branch `feature/projects`
- **Tools page** — `/tools/<tool-name>/` for small self-contained clinical/professional tools. **Client-side only**, see the Publication Policy above. First planned tool: emergency contraception consultation aid. Feature branch `feature/tools`
- **Remove SQLite and the Django admin** — the app defines no models, so the database, `django.contrib.admin` and the `migrate` build step serve nothing while adding build time and exposing `/admin/`
- **Drop Bootstrap** — replace the CDN and the inline `<style>` block with `static/style.css`

**Last Updated:** 2026-08-06
**Architecture:** Django + Markdown files, no content DB
**Python Version:** 3.13
**Django Version:** 6.x
