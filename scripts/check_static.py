"""Check exported pages in Chromium without external network requests."""

import argparse
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.urls import LEGACY_REDIRECT_PATHS  # noqa: E402


def discover_note_paths(directory: Path) -> list[str]:
    writings_dir = directory / 'writings'
    if not writings_dir.is_dir():
        return []
    return [
        f'/writings/{entry.name}/'
        for entry in sorted(writings_dir.iterdir())
        if entry.is_dir() and (entry / 'index.html').is_file()
    ]


def main():
    parser = argparse.ArgumentParser(description='Verify exported static site in headless Chromium.')
    parser.add_argument('--directory', type=Path, default=REPO_ROOT / 'dist')
    args = parser.parse_args()

    directory = args.directory.resolve()
    assert (directory / 'index.html').exists(), f'Run manage.py export_static first ({directory}).'

    note_paths = discover_note_paths(directory)
    assert note_paths, f'No exported notes found under {directory / "writings"}'
    paths = ['/', '/writings/', *note_paths]

    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    errors = []
    external = []
    try:
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
            count = 0
            for path in paths:
                for width in [1440, 390]:
                    page.set_viewport_size({'width': width, 'height': 900})
                    page.goto(origin + path)
                    page.evaluate('document.fonts.ready')
                    for theme, paper in [('light', 'rgb(247, 246, 242)'), ('dark', 'rgb(23, 25, 28)')]:
                        page.emulate_media(media='screen')
                        page.evaluate('(theme) => document.documentElement.dataset.bsTheme = theme', theme)
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
                        else:
                            prose = page.locator('.article p, .sk-section-block p').first
                            assert 'IBM Plex Serif' in prose.evaluate('(el) => getComputedStyle(el).fontFamily')
                            assert prose.evaluate('(el) => getComputedStyle(el).fontSize') == '16px'
                            assert page.evaluate('document.fonts.check(\'16px "IBM Plex Serif"\')')
                        if path == '/':
                            assert page.locator('.site-header').evaluate('(el) => getComputedStyle(el).maxWidth') == '760px'
                            assert page.locator('.sk-spatial-shell').first.bounding_box()['width'] <= 760
                            assert page.locator('.sk-header-socials a').count() == 5
                            assert 'IBM Plex Mono' in page.locator('.sk-meta-line').first.evaluate('(el) => getComputedStyle(el).fontFamily')
                            assert page.evaluate('document.fonts.check(\'14px "IBM Plex Mono"\')')
                            assert page.locator('hr').count() == 0
                        elif path in note_paths:
                            assert page.locator('.site-header').evaluate('(el) => getComputedStyle(el).maxWidth') == '1120px'
                            if width == 1440:
                                assert page.locator('.reading-margin').evaluate('(el) => getComputedStyle(el).paddingTop') == '230px'
                            else:
                                assert not page.locator('.reading-margin').is_visible()
                            page.get_by_text('AI contribution', exact=True).click()
                            assert page.locator('details').first.get_attribute('open') is not None
                            page.get_by_text('AI contribution', exact=True).click()
                            if page.locator('.article hr').count() > 0:
                                assert page.locator('.article hr').first.is_visible()
                        count += 1
                        for mode in ['colour', 'greyscale', 'black-white']:
                            page.evaluate('(mode) => document.documentElement.dataset.printMode = mode', mode)
                            page.emulate_media(media='print')
                            assert not page.locator('.site-header').is_visible()
                            assert page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                            count += 1
                        page.emulate_media(media='screen')

            for slug in LEGACY_REDIRECT_PATHS:
                page.goto(f'{origin}/{slug}/')
                page.wait_for_url(origin + '/')
                count += 1

            assert not external, external
            assert not errors, errors
            browser.close()
            print(f'{count} rendered checks passed across {len(paths)} pages and {len(LEGACY_REDIRECT_PATHS)} static redirects; no external requests or browser errors.')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
