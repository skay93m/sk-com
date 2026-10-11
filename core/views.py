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
                "Disallow: /planning/\n"
                "Crawl-delay: 1\n"
            )
        return HttpResponse(content, content_type='text/plain')


ALLOWED_FONTS = {'baseline', 'c', 'a'}


def _time_to_row(time_str: str) -> int:
    """Convert HH:MM string to 1-based 15-minute grid row (00:00 is row 1, 24:00 is row 97)."""
    parts = time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    total_minutes = h * 60 + m
    # Round to nearest 15-minute quarter hour
    quarter = round(total_minutes / 15)
    return quarter + 1


class PlanningSyntheticView(TemplateView):
    template_name = 'planning.html'

    def get(self, request, *args, **kwargs):
        scenario = request.GET.get('scenario', 'fresh')
        font = request.GET.get('font', 'baseline')

        if font not in ALLOWED_FONTS:
            raise Http404(f"Unknown font: {font}")

        from .planning import load_scenario_snapshot
        try:
            snapshot, simulated_now = load_scenario_snapshot(scenario)
        except (ValueError, FileNotFoundError):
            raise Http404(f"Unknown scenario: {scenario}")

        # Group blocks and items by day for weekly spread rendering
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_data = []
        for day in weekdays:
            # Process blocks with calculated grid row start and span
            day_blocks = []
            for b in snapshot.blocks:
                if b.get('day') == day:
                    b_copy = dict(b)
                    r_start = _time_to_row(b['start'])
                    r_end = _time_to_row(b['end'])
                    r_span = max(1, r_end - r_start)
                    b_copy['row_start'] = r_start
                    b_copy['row_span'] = r_span
                    day_blocks.append(b_copy)
            day_blocks.sort(key=lambda b: b.get('start', ''))

            # Gather day tasks: items with this day + daily recurring + weekly recurring for this day
            day_tasks = []
            for it in snapshot.items:
                if it.get('day') == day:
                    day_tasks.append({
                        'title': it.get('title'),
                        'kind': it.get('kind'),
                        'is_recurring': False,
                    })

            for rec in snapshot.recurring:
                cadence = rec.get('cadence')
                if cadence == 'daily' or (cadence == 'weekly' and day in rec.get('days', [])):
                    day_tasks.append({
                        'title': rec.get('title'),
                        'kind': cadence,
                        'is_recurring': True,
                    })

            days_data.append({
                'name': day,
                'slug': day.lower(),
                'blocks': day_blocks,
                'tasks': day_tasks,
            })

        weekly_goals = [it for it in snapshot.items if not it.get('day')]

        context = {
            'snapshot': snapshot,
            'scenario': scenario,
            'font': font,
            'simulated_now': simulated_now,
            'days_data': days_data,
            'weekly_goals': weekly_goals,
            'all_scenarios': ['fresh', 'stale', 'empty', 'failed'],
            'all_fonts': ['baseline', 'c', 'a'],
            'timeline_hours': list(range(25)),
        }
        response = self.render_to_response(context)
        response['X-Robots-Tag'] = 'noindex'
        return response
