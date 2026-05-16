import re
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import markdown
import yaml
from django.conf import settings


FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

_cache: Optional[list[dict]] = None
_projects_cache: Optional[dict] = None  # keyed by slug


def _normalise_date(value) -> Optional[date]:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _parse_lab_file(path: Path) -> Optional[dict]:
    try:
        raw = path.read_text(encoding='utf-8')
    except OSError:
        return None

    match = FRONTMATTER_RE.match(raw)
    if not match:
        return None

    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not all(k in meta for k in ('title', 'date', 'slug', 'type', 'project')):
        return None

    if str(meta['type']).lower() != 'lab':
        return None

    parsed_date = _normalise_date(meta['date'])
    if parsed_date is None:
        return None

    body_html = markdown.markdown(raw[match.end():], extensions=['extra', 'nl2br'])
    return {
        'title': str(meta['title']),
        'date': parsed_date,
        'slug': str(meta['slug']),
        'type': 'lab',
        'project': str(meta['project']),
        'body_html': body_html,
        'tools': list(meta.get('tools') or []),
        'objectives': list(meta.get('objectives') or []),
        'skills': list(meta.get('skills') or []),
    }


def _load_projects() -> dict:
    global _projects_cache
    if _projects_cache is not None:
        return _projects_cache
    path = settings.CONTENT_DIR / 'labs' / 'projects.yaml'
    if not path.exists():
        _projects_cache = {}
        return _projects_cache
    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or []
    except (OSError, yaml.YAMLError):
        _projects_cache = {}
        return _projects_cache
    _projects_cache = {p['slug']: p for p in data if 'slug' in p and 'name' in p}
    return _projects_cache


def _load_labs() -> list[dict]:
    global _cache
    if _cache is not None:
        return _cache
    labs_dir = settings.CONTENT_DIR / 'labs'
    if not labs_dir.exists():
        _cache = []
        return _cache
    labs = [l for path in labs_dir.glob('*.md') if (l := _parse_lab_file(path)) is not None]
    labs.sort(key=lambda l: l['date'], reverse=True)
    _cache = labs
    return _cache


def get_all_labs() -> list[dict]:
    return _load_labs()


def get_lab_by_slug(slug: str) -> Optional[dict]:
    return next((l for l in _load_labs() if l['slug'] == slug), None)


def get_labs_grouped_by_project() -> list[dict]:
    projects = _load_projects()
    labs = [l for l in _load_labs() if l['project'] in projects]

    grouped: dict = {}
    for lab in labs:
        slug = lab['project']
        if slug not in grouped:
            grouped[slug] = {**projects[slug], 'labs': [], 'latest_date': None}
        grouped[slug]['labs'].append(lab)
        if grouped[slug]['latest_date'] is None or lab['date'] > grouped[slug]['latest_date']:
            grouped[slug]['latest_date'] = lab['date']

    return sorted(grouped.values(), key=lambda p: p['latest_date'], reverse=True)
