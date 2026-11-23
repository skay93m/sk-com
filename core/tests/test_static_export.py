from hashlib import sha256
from html.parser import HTMLParser

import pytest
import yaml
from django.core.management import CommandError, call_command


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
    assert (output / 'index.html').is_file()
    assert (output / 'writings/hello-world/index.html').is_file()
    assert (output / 'static/fonts/IBMPlexSerif-Regular.ttf').is_file()
    assert b'Back to homepage' in (output / 'writings/hello-world/index.html').read_bytes()
    assert b'Long-form notes' in (output / 'index.html').read_bytes()
    assert not (output / 'cv/index.html').exists()
    assert (output / 'robots.txt').is_file()
    for page in output.rglob('*.html'):
        parser = AssetLinks()
        parser.feed(page.read_text())
        for asset in parser.assets:
            assert asset.startswith('/') and not asset.startswith('//')
            assert (output / asset.lstrip('/')).is_file()

    def digests():
        return {str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest()
                for p in output.rglob('*') if p.is_file()}

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
    with open('render.yaml') as source:
        config = yaml.safe_load(source)
    assert config['previews']['generation'] == 'off'
    service = config['services'][0]
    assert service['runtime'] == 'static'
    assert service['staticPublishPath'] == 'dist'
    assert service['previews']['generation'] == 'off'
    routes = {r['source']: r['destination'] for r in service['routes']}
    for path in ['/cv/', '/labs/', '/about/', '/writing/']:
        assert routes[path] == '/'
