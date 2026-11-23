"""Export published pages without running a production Django process."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.shortcuts import render
from django.test import RequestFactory
from django.urls import resolve, reverse

from core.labs import get_all_labs
from core.posts import get_all_posts
from core.urls import LEGACY_REDIRECT_PATHS
from core.views import HomeView, LabDetailView, PostDetailView, RobotsTxtView, WritingsView


class Command(BaseCommand):
    help = 'Export the public site and local assets to dist (no database needed).'

    def add_arguments(self, parser):
        parser.add_argument('--output', default='dist')

    def _export_target(self, staging: Path, url: str) -> Path:
        relative = url.lstrip('/')
        if '..' in Path(relative).parts:
            raise CommandError(f'Unsafe export path: {url}')
        target = staging / relative
        if url.endswith('/'):
            target /= 'index.html'
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def handle(self, *args, **options):
        output = Path(options['output']).absolute()
        marker = '.sk-static-export'
        if output.is_symlink() or (output.exists() and not (output / marker).is_file()):
            raise CommandError('Output must be absent or a previous static export.')
        output.parent.mkdir(parents=True, exist_ok=True)

        pages = [
            ('/', HomeView, {}),
            ('/writings/', WritingsView, {}),
            ('/robots.txt', RobotsTxtView, {}),
        ]
        for items, name, view in [
            (get_all_posts(), 'core:post-detail', PostDetailView),
            (get_all_labs(), 'core:lab-detail', LabDetailView),
        ]:
            for item in items:
                pages.append((reverse(name, args=[item['slug']]), view, {'slug': item['slug']}))

        redirect_urls = [reverse(f'core:{slug}') for slug in LEGACY_REDIRECT_PATHS]

        with TemporaryDirectory(dir=output.parent) as temporary:
            staging = Path(temporary) / 'site'
            staging.mkdir()
            factory = RequestFactory()
            for url, view, kwargs in pages:
                target = self._export_target(staging, url)
                response = view.as_view()(factory.get(url), **kwargs)
                if hasattr(response, 'render'):
                    response.render()
                if response.status_code != 200:
                    raise CommandError(f'Export failed: {url} ({response.status_code})')
                target.write_bytes(response.content)

            for url in redirect_urls:
                request = factory.get(url)
                match = resolve(url)
                response = match.func(request, *match.args, **match.kwargs)
                if response.status_code not in {301, 302}:
                    raise CommandError(f'Expected redirect for {url} (got {response.status_code})')
                target = self._export_target(staging, url)
                fallback = render(request, 'redirect.html', {'target_url': response['Location']})
                target.write_bytes(fallback.content)

            shutil.copytree(settings.BASE_DIR / 'static', staging / 'static')
            (staging / marker).write_text('Stage 1 static export\n')
            if output.exists():
                shutil.rmtree(output)
            staging.rename(output)

        total = len(pages) + len(redirect_urls)
        self.stdout.write(self.style.SUCCESS(f'Exported {total} routes to {output}'))
