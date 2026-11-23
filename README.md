# sk-com

Source for [syafiqkay.com](https://syafiqkay.com), the personal site of Syafiq Kay.

Django 6 renders the homepage and published Markdown notes. A deterministic export
produces HTML and local CSS/font assets for a Render Static Site. No Django process,
database, analytics, runtime JavaScript or external font service is needed to serve
the exported site.

## Local development

Use Python 3.13 and uv:

```bash
uv sync --frozen
export DJANGO_SECRET_KEY="local-development-only-key"
export DEBUG="True"
export ALLOWED_HOSTS="localhost,127.0.0.1"
uv run python manage.py runserver
```

Restart Django after editing content because Markdown is cached in memory.

## Routes

| Route | Behaviour |
| --- | --- |
| `/` | Stage 1 homepage |
| `/writings/<slug>/` | Published note, using the Reading layout |
| `/writings/` | Preserved published writing index |
| `/cv/`, `/labs/`, `/about/`, `/writing/` | Django HTTP 302 to `/` (static export includes `<meta http-equiv="refresh">` fallback HTML) |
| `/labs/<slug>/` | Preserved published lab URLs |

LinkedIn is the canonical career record. The local CV is retired.

## Static export and verification

The deployment check can run without a configured secret:

```bash
uv run pytest -q && uv run python manage.py check --deploy --fail-level WARNING
```

Only `check --deploy` generates a temporary signing key when `DJANGO_SECRET_KEY`
is absent. It does not store the key. A supplied key is checked as configured.
Server startup and static export still require an explicit key. The check without
a supplied key validates configuration, but cannot validate the deployment secret.
Use production settings and a generated key for export and browser verification:

```bash
export DEBUG="False"
export DJANGO_SECRET_KEY="$(uv run python -c 'import secrets; print(secrets.token_urlsafe(64))')"
uv run pytest -q
uv run python manage.py check --deploy --fail-level WARNING
uv run python manage.py export_static
uv run playwright install chromium
uv run python scripts/check_static.py
uv run python -m http.server 8000 --directory dist
```

The exporter writes `dist/` by default, or an explicit `--output` directory. It
replaces only directories marked as previous exports and removes stale pages.
It exports all published notes, the existing writing index and lab detail pages,
static `<meta http-equiv="refresh">` redirect fallbacks for `/cv/`, `/labs/`,
`/about/`, and `/writing/`, `robots.txt`, and local assets. It does not export
admin or retired CV content.

The Chromium check blocks external requests and checks desktop and 390px layouts,
light and D1 dark tokens, F3 typography, disclosure controls, and colour, greyscale,
and black-and-white print modes. Dark tokens are available via
`data-bs-theme="dark"`; Stage 1 has no theme-switching interface.
CI runs the suite, deployment checks, export, and Chromium smoke check.

## Render cutover

`render.yaml` describes the proposed free Static Site, with `dist` as its publish
directory and both Blueprint and service PR previews disabled. It is not currently
synced to the live dashboard. Changing this file does not disable existing paid
services or their previews.

The deployment owner must create/adopt the Static Site, disable PR previews on the
existing Docker service, verify the output, transfer custom domains, and retire the
paid service after the new site is verified. There is no database to migrate for
public pages.

Render's documented static redirect rules return **301** (no status-code field is
exposed in the Blueprint schema), and Render Static Sites always serve existing
physical files before evaluating route rules. `render.yaml` therefore uses uniform
`type: rewrite` rules mapping `/cv`, `/labs`, `/about`, `/writing` (and subpath
wildcards) to `export_static`'s `<meta http-equiv="refresh" content="0; url=/">`
fallback pages (`dist/{cv,labs,about,writing}/index.html`), avoiding permanent
`301` browser caching while preserving physical `/labs/<slug>/` files. Django
implements and tests true HTTP **302** for all four routes; resolve this static
HTTP `302` hosting constraint before cutover if edge HTTP `302` responses are
required, and do not describe Render static site responses as `302`.
See [Render redirect rules](https://render.com/docs/redirects-rewrites) and
[Blueprint configuration](https://render.com/docs/blueprint-spec).

## Design assets and content

The stylesheet ports the selected Stage 1 SK Design System baseline (F3 IBM Plex,
D1 dark tokens, coral-dot mark, 760px homepage, Reading pattern). Fonts are
self-hosted in `static/fonts/` with their SIL Open Font Licence texts.
Published text and dates remain authoritative in `content/`. Optional
`ai_disclosure` frontmatter is shown in Reading provenance when set; when
omitted or blank, the AI contribution disclosure is omitted with no boilerplate
fallback.

Publication is governed by [AGENTS.md](AGENTS.md). Do not import private notes or
planning documents into this repository. All changes go through a pull request.
Never push directly to `main`.
