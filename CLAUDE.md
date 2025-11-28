# CLAUDE.md - AI Assistant Guide for sk-website

## Project Overview

**Project Name:** sk-website (version 4.0.0)
**Purpose:** Personal portfolio website for Syafiq Kay documenting a career exploration journey through "working identity tests"
**Live Site:** https://syafiqkay.com
**Type:** Django web application showcasing systematic career path experiments (pharmacy, law, cybersecurity, actuary)

## Technology Stack

### Backend
- **Python:** 3.13 (see `.python-version`)
- **Framework:** Django 5.2.4
- **WSGI Server:** Gunicorn 20.1.0+
- **Database:** PostgreSQL (production), SQLite (local development)
- **Package Manager:** UV (Astral's fast Python package manager)

### Frontend
- **Template Engine:** Django Templates
- **CSS Framework:** Bootstrap 5 (django-bootstrap-v5 1.0.11+)
- **Styling:** Inline CSS with custom CSS variables
- **No JavaScript files or external static assets**

### Key Dependencies
```
django>=4.0.0
django-bootstrap-v5>=1.0.11
gunicorn>=20.1.0
psycopg2-binary>=2.9.0
dj-database-url>=2.0.0
whitenoise>=6.0.0
python-dotenv>=1.0.0
pytest>=8.4.1
commitizen>=4.8.3
```

## Directory Structure

```
sk-com/
├── manage.py                      # Django management script
├── pyproject.toml                 # Project config & dependencies
├── uv.lock                        # UV package lock file
├── Dockerfile                     # Container configuration
├── render.yaml                    # Render.com deployment config
├── .python-version                # Python 3.13
├── portfolio/                     # Main Django app
│   ├── models.py                  # Database models (WorkingIdentity, IdentityFeed)
│   ├── views.py                   # Views (PortfolioView, IdentityDetailView)
│   ├── urls.py                    # App-level URL routing
│   ├── admin.py                   # Django admin configuration
│   ├── management/commands/
│   │   └── populate_identities.py # Data seeding command
│   ├── migrations/
│   │   └── 0001_initial.py        # Initial database schema
│   └── templates/
│       ├── portfolio.html         # Homepage template
│       └── identity_detail.html   # Identity detail page
└── sk/                            # Django project configuration
    ├── settings.py                # Django settings (159 lines)
    ├── urls.py                    # Root URL configuration
    ├── views.py                   # Robots.txt view
    ├── wsgi.py                    # WSGI configuration
    ├── asgi.py                    # ASGI configuration
    └── templates/
        └── base.html              # Base template with styling
```

## Development Workflows

### Initial Setup

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set environment variables (create .env file or export)
export DJANGO_SECRET_KEY="your-secret-key-here"
export DEBUG="True"
export ALLOWED_HOSTS="localhost,127.0.0.1"

# Run migrations
uv run python manage.py migrate

# Populate initial data
uv run python manage.py populate_identities

# Create superuser
uv run python manage.py createsuperuser

# Run development server
uv run python manage.py runserver
```

### Common Commands

```bash
# Database operations
uv run python manage.py makemigrations    # Create migrations
uv run python manage.py migrate           # Apply migrations
uv run python manage.py shell             # Django shell

# Testing
uv run pytest                             # Run tests
uv run python manage.py test              # Django test runner

# Static files
uv run python manage.py collectstatic     # Collect static files

# Data management
uv run python manage.py populate_identities  # Seed database
```

### Docker Development

```bash
# Build image
docker build -t sk-website .

# Run container
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="your-secret-key" \
  -e DEBUG="True" \
  sk-website
```

## Database Models

### WorkingIdentity Model
**Location:** `portfolio/models.py`

Represents one of the four career identity experiments.

**Fields:**
- `identity`: CharField (unique) - Choices: pharmacy, law, cybersecurity, actuary
- `description`: CharField(200) - e.g., "Foundation identity"
- `experiment_plan`: TextField - Structured plan with aim, hypothesis, methods
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

**Methods:**
- `latest_entry()`: Returns most recent IdentityFeed entry

### IdentityFeed Model
**Location:** `portfolio/models.py`

Represents progress updates for each identity.

**Fields:**
- `working_identity`: ForeignKey(WorkingIdentity) - Related name: 'feed_entries'
- `date`: DateTimeField (auto)
- `status`: TextField - Current status/progress
- `next_action`: TextField - Planned next steps
- `notes`: TextField (optional) - Additional notes

**Ordering:** Descending by date (newest first)

## URL Structure

### Routes
- `/` - Homepage (PortfolioView)
- `/<identity>/` - Identity detail (pharmacy, law, cybersecurity, actuary)
- `/admin/` - Django admin interface
- `/robots.txt` - Robots.txt view

### Examples
- `https://syafiqkay.com/pharmacy/` - Pharmacy identity detail
- `https://syafiqkay.com/cybersecurity/` - Cybersecurity identity detail

## Views and Templates

### PortfolioView (`portfolio/views.py:6-24`)
- **Type:** TemplateView
- **Template:** `portfolio.html`
- **Context:** All WorkingIdentity objects with latest feed entries
- **Purpose:** Homepage showing all four identities with latest updates

### IdentityDetailView (`portfolio/views.py:27-38`)
- **Type:** TemplateView
- **Template:** `identity_detail.html`
- **Context:** Specific WorkingIdentity and all its feed entries
- **URL Parameter:** `identity` (must match model choices)
- **Purpose:** Detail page with experiment plan and full progress feed

### Template Inheritance
- **Base:** `sk/templates/base.html` - Contains navbar, footer, CSS
- **Children:** Extend base and override `{% block content %}`
- **URL References:** Use `{% url 'portfolio:portfolio' %}` with namespace

## Code Conventions

### Core Coding Principles

This project strictly adheres to two fundamental principles:

#### 1. DRY (Don't Repeat Yourself)
**Definition:** Every piece of knowledge should have a single, unambiguous representation in the system.

**Application:**
- **No duplicate code** - Extract repeated logic into functions/methods/classes
- **Single source of truth** - Configuration in one place (settings.py, environment variables)
- **Reusable components** - Template inheritance (base.html → child templates)
- **Helper methods** - Model methods like `latest_entry()` instead of repeated queries
- **Django abstractions** - Use Django's built-in features instead of reinventing

**Examples:**
```python
# BAD - Repeated logic
def get_pharmacy_latest():
    return IdentityFeed.objects.filter(working_identity__identity='pharmacy').latest('date')

def get_law_latest():
    return IdentityFeed.objects.filter(working_identity__identity='law').latest('date')

# GOOD - DRY principle (actual implementation in WorkingIdentity model)
class WorkingIdentity(models.Model):
    def latest_entry(self):
        """Fetch most recent feed entry for this identity"""
        try:
            return self.feed_entries.latest('date')
        except self.feed_entries.model.DoesNotExist:
            return None
```

#### 2. Clean Code
**Definition:** Code that is easy to read, understand, and maintain.

**Principles:**
- **Meaningful names** - Variables, functions, classes should explain their purpose
- **Small functions** - Each function does one thing well
- **Clear intent** - Code reads like well-written prose
- **No magic numbers** - Use named constants or settings
- **Proper formatting** - Consistent indentation, spacing, line length
- **Comments when needed** - Explain why, not what
- **Error handling** - Graceful degradation and clear error messages

**Examples:**
```python
# BAD - Unclear, not clean
def p():
    return IdentityFeed.objects.filter(wi__i='p').order_by('-d')[:1]

# GOOD - Clean code (as implemented in the WorkingIdentity.latest_entry() method)
def get_latest_pharmacy_update():
    """Return the most recent feed entry for the pharmacy identity."""
    pharmacy = WorkingIdentity.objects.filter(identity='pharmacy').first()
    return pharmacy.latest_entry() if pharmacy else None
```

**Code Review Checklist:**
- [ ] Does this violate DRY? Can it be extracted/reused?
- [ ] Is the code self-explanatory? Can I understand it in 30 seconds?
- [ ] Are names descriptive and meaningful?
- [ ] Is the function/method doing only one thing?
- [ ] Could a junior developer understand this code?
- [ ] Is this the simplest solution that works?

### Django Best Practices
- **App Organization:** Single 'portfolio' app for main functionality
- **Template Naming:** Lowercase filenames (e.g., `portfolio.html`, not `Portfolio.html`)
- **URL Namespacing:** Use `app_name = 'portfolio'` in urls.py
- **Model Methods:** Add helper methods like `latest_entry()` for common queries
- **Admin Inline:** Use InlineModelAdmin for related models (IdentityFeed)

### Styling Conventions
- **No external CSS files:** All styling in `base.html` template
- **Bootstrap 5:** Use Bootstrap classes for layout and components
- **CSS Variables:** Custom properties defined in `:root` selector
- **Color Scheme:**
  - Primary: `#2563eb` (blue)
  - Text dark: `#1f2937`
  - Text light: `#6b7280`
  - Background: `#f9fafb`
  - Border: `#e5e7eb`

### File Naming
- **Python Files:** Lowercase with underscores (e.g., `populate_identities.py`)
- **Templates:** Lowercase with underscores or hyphens (e.g., `identity_detail.html`)
- **No uppercase in filenames:** Prevents case-sensitivity issues across platforms

## Environment Variables

### Required
- `DJANGO_SECRET_KEY` - Django secret key (required in production)

### Optional with Defaults
- `DEBUG` - Set to "True" for development (default: "False")
- `ALLOWED_HOSTS` - Comma-separated hostnames (default: "")
- `DATABASE_URL` - Full PostgreSQL connection string (overrides individual DB vars)

### Database Variables (if DATABASE_URL not set)
- `DB_NAME` (default: "sk_website")
- `DB_USER` (default: "postgres")
- `DB_PASSWORD` (default: "")
- `DB_HOST` (default: "localhost")
- `DB_PORT` (default: "5432")

### Security Variables (Production)
All default to "False" in development, "True" in production:
- `SECURE_SSL_REDIRECT`
- `SECURE_HSTS_SECONDS` (31536000 in production)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`

## Testing

### Framework
- **Primary:** Pytest 8.4.1+
- **Alternative:** Django test runner

### Current State
- Test infrastructure in place
- Security features disabled during tests
- Test file: `portfolio/tests.py` (placeholder)

### Running Tests
```bash
uv run pytest                    # Pytest
uv run python manage.py test     # Django test runner
```

## Deployment

### Platform
- **Host:** Render.com
- **Config:** `render.yaml`
- **Database:** PostgreSQL (free tier)
- **Domains:**
  - sk-website.onrender.com
  - syafiqkay.com
  - www.syafiqkay.com

### Build Process
1. Install UV: `pip install uv`
2. Sync dependencies: `uv sync`
3. Run migrations: `uv run python manage.py migrate`
4. Collect static files: `uv run python manage.py collectstatic --noinput`

### Start Command
```bash
uv run gunicorn sk.wsgi:application --bind 0.0.0.0:$PORT
```

### Docker Build Notes
- Uses Python 3.13-slim base image
- Runs collectstatic during build with temporary secret key
- Binds to PORT environment variable (default 8000)

## Git Workflow

### Git Flow Model (Simplified)

This project uses a **simplified Git Flow** workflow without the git-flow package. We use standard git commands to maintain clean branch management.

#### Branch Structure

**Main Branches:**
- `main` - Production-ready code, always deployable
- `develop` - Integration branch for features (optional for this small project)

**Supporting Branches:**
- `feature/*` - New features or enhancements
- `hotfix/*` - Urgent production fixes
- `claude/*` - AI assistant work branches

#### Workflow Commands

**Starting a New Feature:**
```bash
# Create and switch to feature branch from main
git checkout main
git pull origin main
git checkout -b feature/feature-name

# Do your work, commit changes
git add .
git commit -m "feat: add new feature"

# Push feature branch
git push -u origin feature/feature-name

# When ready, merge to main (or create PR)
git checkout main
git merge feature/feature-name
git push origin main

# Delete feature branch after merge
git branch -d feature/feature-name
git push origin --delete feature/feature-name
```

**Hotfix Workflow:**
```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/fix-name

# Fix the issue and commit
git add .
git commit -m "fix: resolve critical issue"

# Merge back to main
git checkout main
git merge hotfix/fix-name
git push origin main

# Delete hotfix branch
git branch -d hotfix/fix-name
git push origin --delete hotfix/fix-name
```

**AI Assistant Branches:**
```bash
# Claude Code creates branches automatically
# Pattern: claude/<description>-<session-id>
# These follow the same merge workflow as feature branches
```

#### Branch Naming Conventions

- `feature/user-authentication` - New features
- `feature/add-contact-form` - Feature additions
- `hotfix/fix-login-bug` - Critical fixes
- `hotfix/security-patch` - Security updates
- `claude/<description>-<session-id>` - AI assistant work

#### Best Practices

1. **Keep commits atomic** - One logical change per commit
2. **Pull before push** - Always pull latest changes before pushing
3. **Delete merged branches** - Clean up after merging
4. **Never force push to main** - Protect the main branch
5. **Test before merging** - Ensure all tests pass before merge
6. **Use meaningful branch names** - Describe what the branch does

### Conventional Commits
- **Tool:** Commitizen 4.8.3+
- **Format:** `<type>: <description>`
- **Types:** feat, fix, docs, style, refactor, test, chore
- **Version Tags:** `v$version`

### Branch Naming
- Feature branches: `feature/<description>` or `claude/<description>-<session-id>`
- Hotfix branches: `hotfix/<description>`
- Always develop on designated branch
- Push with: `git push -u origin <branch-name>`

### Recent Fixes
- Template naming: Portfolio.html → portfolio.html (500 error fix)
- Docker collectstatic: Added build-time secret key
- StaticFiles warnings: Configuration fixes

## Important Notes for AI Assistants

### Critical Do's
1. **Always read files before editing:** Use Read tool before Edit/Write
2. **Use lowercase template names:** `portfolio.html`, not `Portfolio.html`
3. **Preserve exact indentation:** Match existing code style
4. **Test before committing:** Run server and check for errors
5. **Use UV commands:** Prefix with `uv run` for all Python commands
6. **Check database setup:** Ensure migrations applied before testing
7. **Verify environment vars:** Check required variables are set

### Critical Don'ts
1. **Don't create uppercase template files:** Causes 500 errors on production
2. **Don't skip migrations:** Always run migrate after model changes
3. **Don't hardcode secrets:** Use environment variables
4. **Don't modify .gitignore:** Static files and .env should stay ignored
5. **Don't use pip directly:** Use UV for all package operations
6. **Don't create unnecessary files:** This is a minimal codebase by design
7. **Don't add external CSS/JS:** Keep styling inline in base.html

### Common Pitfalls
- **Case-sensitive filenames:** Development may work, production fails
- **Missing collectstatic:** Static files won't serve in production
- **Database URL priority:** DATABASE_URL overrides individual DB_ variables
- **Security in development:** SSL redirect disabled by default locally
- **Port binding:** Use $PORT environment variable, not hardcoded 8000

### File Locations Reference
- **Settings:** `sk/settings.py:1-159`
- **Models:** `portfolio/models.py`
- **Views:** `portfolio/views.py`
- **URLs:** `sk/urls.py` and `portfolio/urls.py`
- **Templates:** `sk/templates/base.html`, `portfolio/templates/*.html`
- **Admin:** `portfolio/admin.py`
- **Management Commands:** `portfolio/management/commands/populate_identities.py`

### When Making Changes

1. **Model Changes:**
   - Edit `portfolio/models.py`
   - Run `uv run python manage.py makemigrations`
   - Run `uv run python manage.py migrate`
   - Test with `uv run python manage.py shell`

2. **Template Changes:**
   - Edit templates in `portfolio/templates/` or `sk/templates/`
   - Check inheritance (base.html → child templates)
   - Test rendering with dev server
   - Verify responsive design

3. **View Changes:**
   - Edit `portfolio/views.py`
   - Update URL patterns if needed
   - Test with browser or curl
   - Check context data passed to templates

4. **Static Files:**
   - Add inline CSS to `sk/templates/base.html`
   - Run `uv run python manage.py collectstatic` before deploy
   - No external CSS/JS files (design decision)

5. **Dependencies:**
   - Add to `pyproject.toml` [project.dependencies]
   - Run `uv sync` to update `uv.lock`
   - Test that package imports work
   - Commit both pyproject.toml and uv.lock

## Quick Reference

### Package Management
```bash
uv sync                  # Install dependencies
uv add <package>         # Add new dependency
uv remove <package>      # Remove dependency
uv run <command>         # Run command in UV environment
```

### Django Management
```bash
uv run python manage.py runserver          # Dev server
uv run python manage.py shell              # Django shell
uv run python manage.py dbshell            # Database shell
uv run python manage.py createsuperuser    # Create admin
uv run python manage.py populate_identities # Seed data
```

### Useful Queries
```python
# In Django shell
from portfolio.models import WorkingIdentity, IdentityFeed

# Get all identities
identities = WorkingIdentity.objects.all()

# Get specific identity
pharmacy = WorkingIdentity.objects.get(identity='pharmacy')

# Get latest feed entry
latest = pharmacy.latest_entry()

# Get all feed entries for identity
feed = pharmacy.feed_entries.all()

# Create new feed entry
IdentityFeed.objects.create(
    working_identity=pharmacy,
    status="Making progress",
    next_action="Continue with next experiment"
)
```

## Security & Privacy

**Status:** ✅ APPROVED FOR PUBLIC RELEASE

This repository has undergone comprehensive security and privacy assessment. All sensitive configuration is managed via environment variables, Django security best practices are implemented, and only publicly available information is included in the codebase.

**For complete security details, see:** [`SECURITY.md`](SECURITY.md)

**Security Contact:** See SECURITY.md for vulnerability reporting procedures.

## External Resources

- **LinkedIn CV:** https://www.linkedin.com/in/syafiqkay
- **Blog:** https://syafiqsspace.substack.com/
- **Live Site:** https://syafiqkay.com
- **Admin:** https://syafiqkay.com/admin/

## Project Philosophy

This is a **minimal, focused codebase** by design:
- Total Python code: ~384 lines across all files
- No external static files
- Single-app Django project
- Self-documenting through the website itself
- Evidence-based approach to career exploration

When making changes, preserve this minimalist philosophy. Only add complexity when absolutely necessary.

---

**Last Updated:** 2025-11-28
**Codebase Version:** 4.0.0
**Python Version:** 3.13
**Django Version:** 5.2.4
**Git Workflow:** Simplified Git Flow
**Coding Principles:** DRY & Clean Code
