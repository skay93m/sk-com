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
| `/notes/<slug>/` | Published note, using Folio’s Reading layout |
| `/cv/`, `/labs/`, `/about/`, `/writing/`, `/writings/`, `/notes/` | Django HTTP 302 to `/` (static export includes `<meta http-equiv="refresh">` fallback HTML) |
| Legacy subpaths (except `/notes/<slug>/`) | Django HTTP 302 to `/` |

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
It exports the homepage, published notes, six legacy refresh pages, and
`robots.txt`. Django `collectstatic` collects assets from the pinned Folio package
into `dist/static/folio/`. Admin and labs content are retired.

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
`type: rewrite` rules mapping legacy paths and their subpaths to refresh pages.
Bare `/notes` maps to `/notes/index.html`; there is no `/notes/*` wildcard, so
published note files serve directly. Django implements true HTTP **302** for the
six legacy routes. Resolve this static HTTP `302` hosting constraint before
cutover if edge HTTP `302` responses are required. Render static responses must
not be described as `302`.
See [Render redirect rules](https://render.com/docs/redirects-rewrites) and
[Blueprint configuration](https://render.com/docs/blueprint-spec).

## Design assets and content

Folio 0.2.0 supplies the Homepage and Reading templates, CSS and F3 IBM Plex
fonts through Django app discovery. `pyproject.toml` tracks Folio’s `main` branch,
and `uv.lock` pins the exact reviewed commit. There are no vendored design assets.
The approved baseline uses D1 dark tokens, the coral-dot mark and a 760px homepage.
Published text and dates remain authoritative in `content/notes/`. Types are
`note` and `essay`; legacy `blog` and `article` map to them respectively. Optional
`ai_disclosure` frontmatter is shown in Reading provenance when set; when
omitted or blank, the AI contribution disclosure is omitted with no boilerplate
fallback.

Publication is governed by [AGENTS.md](AGENTS.md). Do not import private notes or
planning documents into this repository. All changes go through a pull request.
Never push directly to `main`.
