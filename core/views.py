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
        ctx['labs'] = get_all_labs()[:5]
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


class PlanningSyntheticView(TemplateView):
    template_name = 'planning.html'

    def get(self, request, *args, **kwargs):
        scenario = request.GET.get('scenario', 'fresh')
        from .planning import load_scenario_snapshot
        try:
            snapshot, simulated_now = load_scenario_snapshot(scenario)
        except (ValueError, FileNotFoundError):
            raise Http404(f"Unknown scenario: {scenario}")

        # Group blocks and items by day for easy template rendering
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_data = []
        for day in weekdays:
            day_blocks = [b for b in snapshot.blocks if b.get('day') == day]
            day_blocks.sort(key=lambda b: b.get('start', ''))
            day_items = [it for it in snapshot.items if it.get('day') == day]
            days_data.append({
                'name': day,
                'slug': day.lower(),
                'blocks': day_blocks,
                'items': day_items,
            })

        unassigned_items = [it for it in snapshot.items if not it.get('day')]

        context = {
            'snapshot': snapshot,
            'scenario': scenario,
            'simulated_now': simulated_now,
            'days_data': days_data,
            'unassigned_items': unassigned_items,
            'all_scenarios': ['fresh', 'stale', 'empty', 'failed'],
        }
        response = self.render_to_response(context)
        response['X-Robots-Tag'] = 'noindex'
        return response
