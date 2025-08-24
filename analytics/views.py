"""
Analytics views for displaying analytics data and reports.
"""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import PageView, DailyStats, PopularPage


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    """
    Main analytics dashboard view.
    """
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Basic stats
        total_views = PageView.objects.count()
        total_unique_visitors = PageView.objects.values('ip_address').distinct().count()
        views_today = PageView.objects.filter(timestamp__date=today).count()
        views_this_week = PageView.objects.filter(timestamp__date__gte=week_ago).count()
        views_this_month = PageView.objects.filter(timestamp__date__gte=month_ago).count()
        
        context.update({
            'total_views': total_views,
            'total_unique_visitors': total_unique_visitors,
            'views_today': views_today,
            'views_this_week': views_this_week,
            'views_this_month': views_this_month,
        })
        
        # Popular pages
        context['popular_pages'] = PopularPage.objects.order_by('-total_views')[:10]
        
        # Recent activity
        context['recent_views'] = PageView.objects.select_related('user').order_by('-timestamp')[:20]
        
        # Bot vs human traffic stats
        week_views = PageView.objects.filter(timestamp__date__gte=week_ago)
        bot_stats = week_views.aggregate(
            total=Count('id'),
            bots=Count('id', filter=Q(is_bot=True)),
            mobile=Count('id', filter=Q(is_mobile=True))
        )
        context['bot_stats'] = bot_stats
        context['human_requests'] = bot_stats['total'] - bot_stats['bots']
        context['desktop_users'] = bot_stats['total'] - bot_stats['mobile']
        
        # Security metrics
        context['blocked_requests'] = 0  # You can implement this based on your security middleware logs
        
        # Performance stats
        performance = week_views.filter(
            response_time_ms__isnull=False
        ).aggregate(
            avg_response_time=Avg('response_time_ms'),
            slow_requests=Count('id', filter=Q(response_time_ms__gt=1000))
        )
        context['performance'] = performance
        
        # Status code distribution
        status_stats = week_views.values('status_code').annotate(
            count=Count('id')
        ).order_by('status_code')
        context['status_stats'] = list(status_stats)
        context['total_requests'] = sum([stat['count'] for stat in status_stats])
        
        # User experience metrics (placeholder for future implementation)
        context['avg_session_duration'] = "2m 34s"  # Placeholder
        context['bounce_rate'] = "32%"  # Placeholder
        
        # Daily views for chart
        daily_views = []
        for i in range(7):
            day = today - timedelta(days=i)
            views = PageView.objects.filter(timestamp__date=day).count()
            daily_views.append({'date': day.strftime('%m/%d'), 'views': views})
        context['daily_views'] = list(reversed(daily_views))
        
        return context


@staff_member_required
def analytics_api_data(request):
    """
    API endpoint for analytics data (for AJAX requests).
    """
    from django.http import JsonResponse
    
    # Get date range from request
    days = int(request.GET.get('days', 7))
    start_date = timezone.now().date() - timedelta(days=days)
    
    # Get page views data
    views_data = PageView.objects.filter(
        timestamp__date__gte=start_date
    ).extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(
        views=Count('id'),
        unique_visitors=Count('ip_address', distinct=True)
    ).order_by('day')
    
    return JsonResponse({
        'views_data': list(views_data),
        'total_views': PageView.objects.filter(timestamp__date__gte=start_date).count(),
    })


@staff_member_required
def export_analytics(request):
    """
    Export analytics data as CSV.
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Timestamp', 'Path', 'Method', 'Status Code', 'IP Address',
        'User Agent', 'Response Time (ms)', 'Is Bot', 'Is Mobile'
    ])
    
    # Get recent data (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    page_views = PageView.objects.filter(timestamp__gte=thirty_days_ago).order_by('-timestamp')
    
    for view in page_views:
        writer.writerow([
            view.timestamp,
            view.path,
            view.method,
            view.status_code,
            view.ip_address,
            view.user_agent[:100],  # Truncate for CSV
            view.response_time_ms,
            view.is_bot,
            view.is_mobile,
        ])
    
    return response
