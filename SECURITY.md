# Security and Privacy

**Repository:** sk-com, serving syafiqkay.com
**Last reviewed:** 2026-08-06

This document describes the security posture of the application as it actually is.
It is not a certification and it carries no approval status. If anything below does
not match the running system, the running system is right and this file is wrong.

## Architecture that this document applies to

- Django 6 on Python 3.13, single app `core`, project package `syafiqkay`
- **No models and no application database.** All content is markdown files under `content/`, parsed and cached in memory
- SQLite exists at `BASE_DIR / db.sqlite3` for Django auth and admin only. It is inside the container, so it is destroyed on every deploy
- No PostgreSQL, no `psycopg2`, no `DATABASE_URL`
- Deployed as a Docker web service on Render, Frankfurt, behind Render's TLS termination
- Static files served by WhiteNoise. Bootstrap 5.3.3 is currently loaded from the jsDelivr CDN with an SRI hash, and is scheduled for removal

## Secrets

Configuration comes from environment variables, read in `syafiqkay/settings.py`.
`DJANGO_SECRET_KEY` is required and the app refuses to start without it.

`.gitignore` excludes `.env*`, `*.sqlite3`, `__pycache__/`, `staticfiles/`, `media/`,
virtualenvs and logs. No secrets are committed to the repository.

The `Dockerfile` uses a throwaway `DJANGO_SECRET_KEY=build-only-key` for `collectstatic`
at image build time. That value never reaches a running server process.

### Incidents, 2026-08-06

Two real findings, both since remediated. Recorded here rather than omitted, because a
security document that only lists successes is not useful.

1. **The production `DJANGO_SECRET_KEY` was a `django-insecure-` development key.** It had been set manually on the Render service rather than generated. Rotated to a 50-character CSPRNG value. The rotation is staged and becomes live on the next deploy, because a running container retains its start-up environment.
2. **A GitHub personal access token was set as `GITHUB_TOKEN` on the web service** and was read by no application code. Revoked at GitHub and removed from the service environment.

Both values were exposed in an assistant session transcript during investigation, which
is why both were rotated or revoked rather than merely removed.

## Application security

- **No models, no ORM queries, no raw SQL.** The SQL injection surface is Django's own auth and session tables
- **Templates** use Django's automatic HTML escaping everywhere except post and lab bodies. `core/posts.py:61` and `core/labs.py:61` render markdown with the `extra` and `nl2br` extensions and no HTML sanitiser, and `post.html:16` and `lab.html:50` output the result through `|safe`. Python-Markdown passes raw HTML through by default, so **anyone who can commit a markdown file can inject arbitrary HTML and script into the page.** This is acceptable only because commit access is limited to the repository owner and every change goes through a reviewed pull request. It stops being acceptable the moment content is accepted from anyone else, at which point a sanitiser such as `bleach` or `nh3` becomes mandatory
- **No file uploads, no `eval`, no `exec`, no `pickle`, no XML parsing, no shell execution on user input**
- **`/admin/` is exposed** and protected by Django auth. Because the database is destroyed on each deploy, no superuser normally survives, so there is usually no account to log in to. It serves no purpose and is scheduled for removal along with SQLite

## Security headers and transport

Set in `syafiqkay/settings.py`, active whenever `DEBUG` is false:

- HTTPS redirect, and `SECURE_PROXY_SSL_HEADER` set for Render's proxy
- HSTS for one year, including subdomains, with preload
- `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE`
- `X_FRAME_OPTIONS = DENY`, content-type nosniff, strict referrer policy, same-origin opener policy
- `CSRF_TRUSTED_ORIGINS` covers `syafiqkay.com`, `www.syafiqkay.com` and `*.onrender.com`

Note that `ALLOWED_HOSTS` has `.onrender.com` appended unconditionally at
`settings.py:29`, so every Render subdomain is accepted regardless of configuration.

## Privacy

The site is governed by the **Publication Policy in `CLAUDE.md`**, which is deny by
default and forbids employer material, patient cases including anonymised ones,
financial detail, and reportage of working life.

`/tools/` pages are **client-side only** by architectural rule. They must not POST,
`fetch`, store or log anything. This exists because the tools are intended for use on a
hotdesking work computer, where clinical detail will be entered into them. Any such data
reaching the server would constitute a patient data flow into a personal website with no
lawful basis, no retention policy and no controller relationship. A tool that sends data
to the server is a defect regardless of whether it works.

## Dependencies

Declared in `pyproject.toml`, pinned in `uv.lock`. Runtime: Django, Gunicorn,
WhiteNoise, Markdown, python-dotenv, PyYAML. Development only, and excluded from the
production image: pytest, pytest-django.

Ten packages reach production. Keeping the runtime surface this small is deliberate.

```bash
uv sync --upgrade   # periodically, then run the tests
```

## Known outstanding items

- Bootstrap is loaded from a third-party CDN. Removing it eliminates that dependency
- `/admin/` and SQLite are still present despite serving nothing
- The container runs as root. Adding a non-root user would be defence in depth

## Reporting

Non-sensitive issues via GitHub Issues. Sensitive issues via the contact route linked
from the site. Expect a response within seven days.

## Review triggers

Re-review before adding authentication, before accepting any user input that reaches the
server, before adding a third-party integration, before shipping the first `/tools/`
page, and on any critical CVE in Django, Gunicorn or WhiteNoise.

## History

An earlier version of this file, dated 2025-11-28, assessed a `portfolio` Django app with
`sk/settings.py`, PostgreSQL and `psycopg2`. None of that has ever existed in this
repository. It also certified that there were no exposed tokens and that the secret key
was platform-generated, both of which were untrue of the running service. It was replaced
wholesale on 2026-08-06.
