# AGENTS.md

Instructions for AI coding agents working on syafiqkay.com. Describes the repo as it is now.

## What this is

Personal site for Syafiq Kay, positioned on the intersection of clinical practice, law and technical work. Content-first and identity-forward. It hosts evidence of ongoing work and is not a brochure. It is a repositioning of a working site, not a rewrite.

Live: https://syafiqkay.com. Source is public.

## Stack

- Python 3.13, Django 6, uv, Gunicorn, WhiteNoise
- Docker on Render (Frankfurt, auto-deploys on merge to `main`). The Render dashboard is authoritative; `render.yaml` is not synced
- Content is markdown with YAML frontmatter in `content/`, cached in memory. Restart the server to see new files
- Django templates and one hand-written stylesheet, `static/style.css`
- SQLite exists only for Django auth and admin. The app has no models

## Layout

```
core/            single Django app: views.py, urls.py, posts.py, labs.py,
                 context_processors.py (bio), templates/, tests/
content/posts/   posts (type: blog | article)
content/labs/    lab write-ups plus projects.yaml
static/          style.css, labs/<slug>/ assets
syafiqkay/       settings, urls, wsgi
.github/workflows/ci.yml   tests and `check --deploy`
.claude/commands/publish.md   the /publish command
```

## Commands

```bash
uv sync
uv run python manage.py runserver
uv run pytest
uv run python manage.py check --deploy --fail-level WARNING
```

Needs `DJANGO_SECRET_KEY`. Set `DEBUG=True` and `ALLOWED_HOSTS=localhost,127.0.0.1` for local work. Use `uv`, never bare `pip`. Production runs `uv run --frozen --no-dev`.

## Routes

`/` home, `/writings/`, `/writings/<slug>/`, `/labs/`, `/labs/<slug>/`, `/cv/`, `/robots.txt`, `/admin/` (to be removed).

Planned: `/now/`, `/tools/<name>/`.

## Content rules

Posts need `title`, `date` (YYYY-MM-DD), `slug`, `type` (`blog` or `article`) and `author: Syafiq Kay`. Labs also need `project` (a slug in `content/labs/projects.yaml`) and `type: lab`. Optional lists: `tools`, `objectives`, `skills`. A file missing a required field or with invalid frontmatter is silently skipped.

- Never change a published `slug`. It is the URL
- Lab assets go in `static/labs/<slug>/`, created by hand
- New content: use `/publish <file>`. It creates `publish/<slug>`, commits and pushes
- CV: edit `core/templates/cv.html`. Bio: edit `core/context_processors.py`

## Publication policy

Deny by default. Content clears every rule or it does not go on the site. If unsure, stop and ask.

1. Nothing about employers: no grievances, disputes, colleagues or internal process.
2. Practice reflections are allowed only if they meet GPhC confidentiality standards. No real encounter is described, even de-identified. Write patterns or clearly labelled composites only. No patient may be identifiable, alone or in combination with other details, including to the patient themselves. Every post that describes practice passes this check before merge:
   - No names, ages, dates, locations, stores or sites, or rare details
   - No detail someone could recognise as their own encounter
   - Specific enough to teach something, general enough to fit many encounters
   - A pattern or composite, never a single real encounter
   - No colleague or employer material (rule 1)

   The agent reviews each such draft against this list and stops to ask if any answer is unclear. The owner decides. The agent never publishes a practice post on its own.
3. No finances.
4. Pharmacy appears as expertise and analysis, never as reportage of working life.
5. Tools receive no user data at the server.
6. Vault-derived content reaches the site only through a reviewed pull request diff, never a live query from the running app.

Sources: GPhC [In practice: guidance on confidentiality](https://assets.pharmacyregulation.org/files/2025-12/gphc-in-practice-guidance-on-confidentiality-updated-november-2025.pdf) and [Demonstrating professionalism online](https://assets.pharmacyregulation.org/files/2024-11/Demonstrating-professionalism-online-January-2024.pdf). The vault copy of this policy in `areas/Website` is authoritative and must match.

## Tools (`/tools/`)

Used on shared work computers, so clinical detail will be typed in. Architectural constraint, not a preference:

- Client-side only: HTML, CSS and vanilla JS. All computation in the browser
- No form POST, `fetch`, XHR or WebSocket to the origin
- No analytics, cookies, or `localStorage`/`sessionStorage` for anything clinical
- No login
- Each page shows a visible statement that nothing entered leaves the device and nothing is stored
- Each page has a clear button, print styles and a mobile-friendly layout

A tool that sends data to the server is a defect even if it works. First planned tool: emergency contraception consultation aid.

## Code conventions

- DRY, small functions, meaningful names. Remove before adding
- Plain CSS in `static/style.css`. No framework, no CDN, no inline `<style>`, no npm, no build step
- No JavaScript site-wide. Vanilla JS only inside a tool page that needs it
- Aesthetic: sharp academic notebook. Single column, serif-ish type
- Palette: tomato `#ff4f40`, lavender grey `#a4a8d1`, powder blue `#a4bfeb`, cool steel `#8cabbe`, space indigo `#34344a`
- Python and template filenames are lowercase with underscores
- Do not add a database, models or secrets in code

Bootstrap 5.3.3 is still loaded from a CDN in `base.html` and `static/style.css` is empty. Do not add new Bootstrap usage. Replacing it with the stylesheet is roadmap step 1.

## Purpose and site plan

The site is a public record of how Syafiq thinks and what he has done across pharmacy, law and technical work. It lets employers, peers and his future self see how the strands connect, and it shows the path over time.

Four sections:

- Writing: what he is thinking about. Each article has a title, description, date and read time
- Labs: what he is experimenting with, as a public research notebook
- CV: what he has done. Clean and conventional (Experience, Education, Projects, Publications, Skills, Professional registrations) with a Download PDF
- About: how the strands fit together

The homepage opens with a statement about problems between disciplines, then routes to Writing and Labs. Look and feel are modelled on docs.basicmemory.com (sidebar navigation, typography, colour) while keeping a bespoke identity.

Decided: stay on Django. Astro with Starlight is not adopted. Revisit only if search or content volume justifies it.

## Roadmap (do only when asked)

1. Look and homepage: stylesheet, drop Bootstrap, new base layout and home page
2. Writing and Labs: docs-style sidebar (Labs grouped by project, Writing by year), description and read time on articles
3. CV: trim to conventional sections, add Download PDF, move the working identity tests to Labs or About
4. About page
5. Cleanup: remove SQLite, admin and the migrate step, add a Content Security Policy
6. `/now/`, curated and separate from any private dashboard
7. CV and bio as data: `content/config/cv.yaml`, `bio.yaml`
8. Evidence backfill: labs and posts
9. CV and `/now/` sync: a weekly export opens a PR, and the diff is the privacy gate. Pages show the real last-sync date
10. `/tools/`

## Principles

- Reality outranks documentation. Fix the doc when the two disagree
- One fact, one home. The vault owns intent. This repo owns implementation
- No runtime coupling between the public site and private systems
- Retire rules explicitly. Do not let them lapse silently
- Fail visibly

## Git

- Never push to `main`. Render deploys every commit to it. Every change goes through a pull request
- Branches: `feature/*`, `hotfix/*`, `chore/*` (config, dependencies, docs, tooling), `claude/*` (AI work that fits nothing else), `publish/<slug>` (one piece of content)
- Prefix describes the kind of change, not who made it
- Conventional Commits: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- CI must pass before merge

## Before you change anything

Read the file first. Run `uv run pytest` before opening a PR.
