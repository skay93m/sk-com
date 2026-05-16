from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView, View
from django.conf import settings

from .posts import get_all_posts, get_post_by_slug
from .labs import get_all_labs, get_lab_by_slug, get_labs_grouped_by_project


class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['posts'] = get_all_posts()[:5]
        return ctx


class WritingsView(TemplateView):
    template_name = 'writings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['posts'] = get_all_posts()
        return ctx


class PostDetailView(TemplateView):
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        post = get_post_by_slug(self.kwargs['slug'])
        if post is None:
            raise Http404
        ctx['post'] = post
        return ctx


class CVView(TemplateView):
    template_name = 'cv.html'


class LabsView(TemplateView):
    template_name = 'labs.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projects'] = get_labs_grouped_by_project()
        return ctx


class LabDetailView(TemplateView):
    template_name = 'lab.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lab = get_lab_by_slug(self.kwargs['slug'])
        if lab is None:
            raise Http404
        ctx['lab'] = lab
        return ctx


@method_decorator(cache_control(max_age=86400), name='dispatch')
class RobotsTxtView(View):
    def get(self, request):
        robots_path = settings.BASE_DIR / 'robots.txt'
        content = None
        if robots_path.exists():
            try:
                content = robots_path.read_text()
            except OSError:
                pass

        if not content:
            content = (
                "User-agent: *\n"
                "Disallow: /admin/\n"
                "Crawl-delay: 1\n"
            )
        return HttpResponse(content, content_type='text/plain')
