"""Check exported pages in Chromium without external network requests."""

import argparse
import sys
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import Page, sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.context_processors import BIO  # noqa: E402
from core.tests.constants import (  # noqa: E402
    AI_CONTRIBUTION_LABEL,
    AI_CONTRIBUTION_SUMMARY,
    FORBIDDEN_AI_DISCLOSURE_TEXT,
    FORBIDDEN_BOUNDARY_TEXT,
    HELLO_WORLD_AI_DISCLOSURE,
    REVISION_HISTORY_LABEL,
)
from core.urls import LEGACY_REDIRECT_PATHS  # noqa: E402

THEME_BACKGROUNDS = (
    ('light', 'rgb(247, 246, 242)'),
    ('dark', 'rgb(23, 25, 28)'),
)
PRINT_MODES = ('colour', 'greyscale', 'black-white')
VIEWPORT_WIDTHS = (1440, 390)


def discover_note_paths(directory: Path) -> list[str]:
    """Return exported note URLs discovered under dist/writings/."""
    writings_dir = directory / 'writings'
    if not writings_dir.is_dir():
        return []
    return [
        f'/writings/{entry.name}/'
        for entry in sorted(writings_dir.iterdir())
        if entry.is_dir() and (entry / 'index.html').is_file()
    ]


@contextmanager
def serve_static_directory(directory: Path):
    """Serve an exported directory locally on an ephemeral localhost port."""
    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()


def _verify_no_boundary_copy(page: Page) -> None:
    """Assert legacy bio and removed boundary copy do not appear in rendered DOM."""
    body_text = page.locator('body').inner_text()
    for forbidden in FORBIDDEN_BOUNDARY_TEXT:
        assert forbidden not in body_text
    assert page.locator('.sk-boundary').count() == 0


def _verify_homepage(page: Page) -> None:
    """Assert homepage layout, typography, and Stage 1 statement paragraphs."""
    assert page.locator('.site-header').evaluate('(el) => getComputedStyle(el).maxWidth') == '760px'
    assert page.locator('.sk-spatial-shell').first.bounding_box()['width'] <= 760
    assert page.locator('.sk-header-socials a').count() == 5
    assert 'IBM Plex Mono' in page.locator('.sk-meta-line').first.evaluate('(el) => getComputedStyle(el).fontFamily')
    assert page.evaluate('document.fonts.check(\'14px "IBM Plex Mono"\')')
    assert page.locator('hr').count() == 0
    statement_text = page.locator('.sk-statement-zone').inner_text()
    assert len(BIO['paragraphs']) == 3
    for paragraph in BIO['paragraphs']:
        assert paragraph in statement_text
    _verify_no_boundary_copy(page)


def _verify_disclosure_toggle(provenance, summary_text: str, expected_text: str | None = None) -> None:
    """Assert a provenance disclosure summary toggles open/closed and shows expected text."""
    summary = provenance.locator('summary', has_text=summary_text)
    assert summary.count() == 1
    details = summary.locator('..')
    summary.click()
    assert details.get_attribute('open') is not None
    if expected_text is not None:
        assert details.locator('p').inner_text() == expected_text
    summary.click()
    assert details.get_attribute('open') is None


def _verify_reading_note(page: Page, path: str, width: int) -> None:
    """Assert Reading layout margin, disclosure controls, and boundary removal."""
    assert page.locator('.site-header').evaluate('(el) => getComputedStyle(el).maxWidth') == '1120px'
    if width == 1440:
        assert page.locator('.reading-margin').evaluate('(el) => getComputedStyle(el).paddingTop') == '230px'
    else:
        assert not page.locator('.reading-margin').is_visible()
    _verify_no_boundary_copy(page)
    assert FORBIDDEN_AI_DISCLOSURE_TEXT not in page.content()
    assert 'Published by Syafiq Kay.' in page.locator('.reading-margin').text_content()

    provenance = page.locator('.article-provenance')
    _verify_disclosure_toggle(provenance, REVISION_HISTORY_LABEL)

    if path == '/writings/hello-world/':
        _verify_disclosure_toggle(provenance, AI_CONTRIBUTION_LABEL, HELLO_WORLD_AI_DISCLOSURE)
        assert page.locator('.article hr').count() == 0
        assert page.locator('.article em').count() == 0
        body_paragraphs_text = '\n'.join(page.locator('.article > p').all_inner_texts())
        assert HELLO_WORLD_AI_DISCLOSURE not in body_paragraphs_text
    elif path == '/writings/controlled-drugs-indelible-ink/':
        assert provenance.locator('summary', has_text=AI_CONTRIBUTION_LABEL).count() == 0
        assert AI_CONTRIBUTION_SUMMARY not in page.content()
    else:
        if provenance.locator('summary', has_text=AI_CONTRIBUTION_LABEL).count() > 0:
            _verify_disclosure_toggle(provenance, AI_CONTRIBUTION_LABEL)
        if page.locator('.article hr').count() > 0:
            assert page.locator('.article hr').first.is_visible()


def verify_screen_layout(page: Page, path: str, width: int, note_paths: list[str], paper: str) -> None:
    """Assert typography, palette, spacing, and responsive layout on screen media."""
    assert page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor') == paper
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert page.locator('.site-header').evaluate('(el) => getComputedStyle(el).borderBottomWidth') == '0px'
    assert page.locator('.sk-site-footer').evaluate('(el) => getComputedStyle(el).borderTopWidth') == '0px'
    assert page.locator('.sk-site-footer').evaluate('(el) => getComputedStyle(el).position') == 'static'
    assert page.locator('.sk-footer-copy').evaluate('(el) => getComputedStyle(el).textAlign') == 'center'
    assert page.locator('.sk-logo span').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(255, 79, 64)'

    if path == '/writings/':
        first_link = page.locator('.content-list-body > a').first
        assert 'IBM Plex Sans' in first_link.evaluate('(el) => getComputedStyle(el).fontFamily')
        assert page.evaluate('document.fonts.check(\'16px "IBM Plex Sans"\')')
        return

    prose = page.locator('.article p, .sk-section-block p').first
    assert 'IBM Plex Serif' in prose.evaluate('(el) => getComputedStyle(el).fontFamily')
    assert prose.evaluate('(el) => getComputedStyle(el).fontSize') == '16px'
    assert page.evaluate('document.fonts.check(\'16px "IBM Plex Serif"\')')

    if path == '/':
        _verify_homepage(page)
    elif path in note_paths:
        _verify_reading_note(page, path, width)


def verify_print_modes(page: Page) -> int:
    """Assert colour, greyscale, and black-white print media rendering."""
    checked = 0
    for mode in PRINT_MODES:
        page.evaluate('(mode) => document.documentElement.dataset.printMode = mode', mode)
        page.emulate_media(media='print')
        assert not page.locator('.site-header').is_visible()
        assert page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checked += 1
    page.emulate_media(media='screen')
    return checked


def verify_legacy_redirects(page: Page, origin: str) -> int:
    """Assert static fallback HTML redirects navigate cleanly to the homepage."""
    checked = 0
    for slug in LEGACY_REDIRECT_PATHS:
        page.goto(f'{origin}/{slug}/')
        page.wait_for_url(origin + '/')
        checked += 1
    return checked


def run_chromium_checks(origin: str, paths: list[str], note_paths: list[str]) -> int:
    """Execute headless Chromium smoke checks with external requests blocked."""
    errors = []
    external = []
    count = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.on('response', lambda response: errors.append(response.url) if response.status >= 400 else None)

        def local_only(route):
            if route.request.url.startswith(origin + '/'):
                route.continue_()
            else:
                external.append(route.request.url)
                route.abort()

        page.route('**/*', local_only)
        for path in paths:
            for width in VIEWPORT_WIDTHS:
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto(origin + path)
                page.evaluate('document.fonts.ready')
                for theme, paper in THEME_BACKGROUNDS:
                    page.emulate_media(media='screen')
                    page.evaluate('(theme) => document.documentElement.dataset.bsTheme = theme', theme)
                    verify_screen_layout(page, path, width, note_paths, paper)
                    count += 1
                    count += verify_print_modes(page)

        count += verify_legacy_redirects(page, origin)
        assert not external, external
        assert not errors, errors
        browser.close()
    return count


def main():
    parser = argparse.ArgumentParser(description='Verify exported static site in headless Chromium.')
    parser.add_argument('--directory', type=Path, default=REPO_ROOT / 'dist')
    args = parser.parse_args()

    directory = args.directory.resolve()
    assert (directory / 'index.html').exists(), f'Run manage.py export_static first ({directory}).'

    note_paths = discover_note_paths(directory)
    assert note_paths, f'No exported notes found under {directory / "writings"}'
    paths = ['/', '/writings/', *note_paths]

    with serve_static_directory(directory) as origin:
        count = run_chromium_checks(origin, paths, note_paths)
    print(
        f'{count} rendered checks passed across {len(paths)} pages and '
        f'{len(LEGACY_REDIRECT_PATHS)} static redirects; no external requests or browser errors.'
    )


if __name__ == '__main__':
    main()
