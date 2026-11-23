from hashlib import sha256
from html.parser import HTMLParser
import re

import pytest
import yaml
from django.conf import settings
from django.core.management import CommandError, call_command
from django.utils.html import escape

from core.context_processors import BIO
from core.posts import get_all_posts
from core.tests.constants import (
    AI_CONTRIBUTION_LABEL,
    AI_CONTRIBUTION_SUMMARY,
    FORBIDDEN_AI_DISCLOSURE_TEXT,
    FORBIDDEN_BOUNDARY_TEXT,
    HELLO_WORLD_AI_DISCLOSURE,
    REVISION_HISTORY_SUMMARY,
)
from core.urls import LEGACY_REDIRECT_PATHS


def _assert_no_boundary_copy(html: str) -> None:
    for forbidden in FORBIDDEN_BOUNDARY_TEXT:
        assert forbidden not in html


def _split_provenance_and_body(html: str) -> tuple[str, str]:
    start = html.find('<div class="article-provenance">')
    assert start != -1
    depth = 0
    end = None
    for tag in re.finditer(r'<(/)?div\b', html[start:]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            close_end = html.find('>', start + tag.end())
            assert close_end != -1
            end = close_end + 1
            break
    assert end is not None
    article_end = html.find('</article>', end)
    assert article_end != -1
    relations_start = html.find('<div class="sk-reading-relations">', end)
    body_end = relations_start if -1 < relations_start < article_end else article_end
    return html[start:end], html[end:body_end]


class AssetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'img'} and attrs.get('src'):
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in {'stylesheet', 'icon', 'preload'}:
            self.assets.append(attrs['href'])


def test_static_export_is_complete_and_repeatable(tmp_path):
    output = tmp_path / 'site'
    call_command('export_static', output=str(output))

    posts = get_all_posts()
    assert posts
    assert (output / 'index.html').is_file()
    assert (output / 'writings/index.html').is_file()
    assert (output / 'static/fonts/IBMPlexSerif-Regular.ttf').is_file()
    index_html = (output / 'index.html').read_text()
    assert 'Long-form notes' in index_html
    assert len(BIO['paragraphs']) == 3
    for paragraph in BIO['paragraphs']:
        assert escape(paragraph) in index_html
    _assert_no_boundary_copy(index_html)
    assert 'sk-boundary' not in (output / 'static/style.css').read_text()
    assert (output / 'robots.txt').is_file()

    slugs = {post['slug'] for post in posts}
    assert {'hello-world', 'controlled-drugs-indelible-ink'} <= slugs

    for post in posts:
        note_html = (output / 'writings' / post['slug'] / 'index.html').read_text()
        assert 'Back to homepage' in note_html
        provenance_html, body_html = _split_provenance_and_body(note_html)
        assert REVISION_HISTORY_SUMMARY in provenance_html
        assert 'Published by Syafiq Kay.' in note_html
        assert FORBIDDEN_AI_DISCLOSURE_TEXT not in note_html
        _assert_no_boundary_copy(note_html)
        if post['ai_disclosure']:
            expected_disclosure = (
                f"<details>{AI_CONTRIBUTION_SUMMARY}<p>{escape(post['ai_disclosure'])}</p></details>"
            )
            assert expected_disclosure in provenance_html
        else:
            assert AI_CONTRIBUTION_SUMMARY not in note_html
            assert AI_CONTRIBUTION_LABEL not in provenance_html

        if post['slug'] == 'hello-world':
            assert post['ai_disclosure'] == HELLO_WORLD_AI_DISCLOSURE
            assert '<hr' not in body_html
            assert '<em>' not in body_html
            assert escape(HELLO_WORLD_AI_DISCLOSURE) not in body_html
            assert note_html.count(escape(HELLO_WORLD_AI_DISCLOSURE)) == 1
        elif post['slug'] == 'controlled-drugs-indelible-ink':
            assert post['ai_disclosure'] is None

    for legacy in LEGACY_REDIRECT_PATHS:
        fallback = (output / legacy / 'index.html').read_text()
        assert 'http-equiv="refresh"' in fallback
        assert 'url=/' in fallback
        assert 'noindex' in fallback
        assert '<script' not in fallback
        assert 'Experience' not in fallback

    for page in output.rglob('*.html'):
        parser = AssetLinks()
        parser.feed(page.read_text())
        for asset in parser.assets:
            assert asset.startswith('/') and not asset.startswith('//')
            assert (output / asset.lstrip('/')).is_file()

    def digests():
        return {
            str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest()
            for p in output.rglob('*')
            if p.is_file()
        }

    first = digests()
    (output / 'stale.html').write_text('old page')
    call_command('export_static', output=str(output))
    assert digests() == first


def test_export_refuses_to_replace_unrelated_directory(tmp_path):
    existing = tmp_path / 'important'
    existing.mkdir()
    (existing / 'keep.txt').write_text('keep')
    with pytest.raises(CommandError, match='previous static export'):
        call_command('export_static', output=str(existing))
    assert (existing / 'keep.txt').read_text() == 'keep'


def test_render_static_configuration():
    render_path = settings.BASE_DIR / 'render.yaml'
    with render_path.open() as source:
        config = yaml.safe_load(source)
    assert config['previews']['generation'] == 'off'
    service = config['services'][0]
    assert service['runtime'] == 'static'
    assert service['staticPublishPath'] == 'dist'
    assert service['previews']['generation'] == 'off'
    assert 'uv==0.11.32' in service['buildCommand']

    assert not any(r['type'] == 'redirect' for r in service['routes'])

    rewrites = {
        r['source']: r['destination']
        for r in service['routes']
        if r['type'] == 'rewrite'
    }
    for slug in LEGACY_REDIRECT_PATHS:
        assert rewrites[f'/{slug}'] == f'/{slug}/index.html'
        assert rewrites[f'/{slug}/*'] == f'/{slug}/index.html'
