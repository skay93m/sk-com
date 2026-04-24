import re
from pathlib import Path
from typing import Optional

import markdown
import yaml
from django.conf import settings


FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

VALID_TYPES = {'blog', 'article'}


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

    body_html = markdown.markdown(raw[match.end():], extensions=['extra', 'nl2br'])
    return {
        'title': str(meta['title']),
        'date': meta['date'],
        'slug': str(meta['slug']),
        'type': str(meta['type']).lower(),
        'body_html': body_html,
    }


def get_all_posts() -> list[dict]:
    posts_dir = settings.CONTENT_DIR / 'posts'
    if not posts_dir.exists():
        return []
    posts = [p for path in posts_dir.glob('*.md') if (p := _parse_post_file(path)) is not None]
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def get_post_by_slug(slug: str) -> Optional[dict]:
    return next((p for p in get_all_posts() if p['slug'] == slug), None)
