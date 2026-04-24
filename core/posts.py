import re
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import markdown
import yaml
from django.conf import settings


FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

VALID_TYPES = {'blog', 'article'}

_cache: Optional[list[dict]] = None


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


def _parse_post_file(path: Path) -> Optional[dict]:
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

    if not all(k in meta for k in ('title', 'date', 'slug', 'type')):
        return None

    if str(meta['type']).lower() not in VALID_TYPES:
        return None

    parsed_date = _normalise_date(meta['date'])
    if parsed_date is None:
        return None

    body_html = markdown.markdown(raw[match.end():], extensions=['extra', 'nl2br'])
    return {
        'title': str(meta['title']),
        'date': parsed_date,
        'slug': str(meta['slug']),
        'type': str(meta['type']).lower(),
        'body_html': body_html,
    }


def _load_posts() -> list[dict]:
    global _cache
    if _cache is not None:
        return _cache
    posts_dir = settings.CONTENT_DIR / 'posts'
    if not posts_dir.exists():
        _cache = []
        return _cache
    posts = [p for path in posts_dir.glob('*.md') if (p := _parse_post_file(path)) is not None]
    posts.sort(key=lambda p: p['date'], reverse=True)
    _cache = posts
    return _cache


def get_all_posts() -> list[dict]:
    return _load_posts()


def get_post_by_slug(slug: str) -> Optional[dict]:
    return next((p for p in _load_posts() if p['slug'] == slug), None)
