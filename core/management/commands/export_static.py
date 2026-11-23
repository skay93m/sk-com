"""Export published pages without running a production Django process."""

import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.test import RequestFactory
from django.urls import reverse

from core.labs import get_all_labs
from core.posts import get_all_posts
from core.views import HomeView, LabDetailView, PostDetailView, RobotsTxtView, WritingsView


class Command(BaseCommand):
    help = 'Export the public site and local assets to dist (no database needed).'

    def add_arguments(self, parser):
        parser.add_argument('--output', default='dist')

    def handle(self, *args, **options):
        output = Path(options['output']).absolute()
        marker = '.sk-static-export'
        if output.is_symlink() or (output.exists() and not (output / marker).is_file()):
            raise CommandError('Output must be absent or a previous static export.')
        output.parent.mkdir(parents=True, exist_ok=True)
        pages = [('/', HomeView, {}), ('/writings/', WritingsView, {}),
                 ('/robots.txt', RobotsTxtView, {})]
        for posts, name, view in [
            (get_all_posts(), 'core:post-detail', PostDetailView),
            (get_all_labs(), 'core:lab-detail', LabDetailView),
        ]:
            for post in posts:
                pages.append((reverse(name, args=[post['slug']]), view, {'slug': post['slug']}))

        with TemporaryDirectory(dir=output.parent) as temporary:
            staging = Path(temporary) / 'site'
            staging.mkdir()
            factory = RequestFactory()
            for url, view, kwargs in pages:
                relative = url.lstrip('/')
                if '..' in Path(relative).parts:
                    raise CommandError(f'Unsafe export path: {url}')
                target = staging / relative
                if url.endswith('/'):
                    target /= 'index.html'
                target.parent.mkdir(parents=True, exist_ok=True)
                response = view.as_view()(factory.get(url), **kwargs)
                if hasattr(response, 'render'):
                    response.render()
                if response.status_code != 200:
                    raise CommandError(f'Export failed: {url} ({response.status_code})')
                target.write_bytes(response.content)
            shutil.copytree(settings.BASE_DIR / 'static', staging / 'static')
            (staging / marker).write_text('Stage 1 static export\n')
            if output.exists():
                shutil.rmtree(output)
            staging.rename(output)
        self.stdout.write(self.style.SUCCESS(f'Exported {len(pages)} pages to {output}'))
