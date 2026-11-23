"""Check exported pages in Chromium without external network requests."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


def main():
    directory = Path('dist').resolve()
    assert (directory / 'index.html').exists(), 'Run manage.py export_static first.'
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
            for path in ['/', '/writings/hello-world/', '/writings/controlled-drugs-indelible-ink/']:
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
                        prose = page.locator('.article p, .sk-section-block p').first
                        assert 'IBM Plex Serif' in prose.evaluate('(el) => getComputedStyle(el).fontFamily')
                        assert prose.evaluate('(el) => getComputedStyle(el).fontSize') == '16px'
                        assert page.evaluate('document.fonts.check(\'16px "IBM Plex Serif"\')')
                        if path == '/':
                            assert page.locator('.sk-spatial-shell').first.bounding_box()['width'] <= 760
                            assert page.locator('.sk-header-socials a').count() == 5
                        else:
                            page.get_by_text('AI contribution', exact=True).click()
                            assert page.locator('details').first.get_attribute('open') is not None
                            page.get_by_text('AI contribution', exact=True).click()
                        count += 1
                        for mode in ['colour', 'greyscale', 'black-white']:
                            page.evaluate('(mode) => document.documentElement.dataset.printMode = mode', mode)
                            page.emulate_media(media='print')
                            assert not page.locator('.site-header').is_visible()
                            assert page.locator('body').evaluate('(el) => getComputedStyle(el).backgroundColor') == 'rgb(255, 255, 255)'
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                            count += 1
                        page.emulate_media(media='screen')
            assert not external, external
            assert not errors, errors
            browser.close()
            print(f'{count} rendered checks passed; no external requests or browser errors.')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
