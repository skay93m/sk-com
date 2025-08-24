"""
Analytics middleware to track HTTP requests and page views.
"""
import time
import re
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.db import transaction
from django.conf import settings


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to track page views and basic analytics.
    """
    
    # Bot user agents patterns
    BOT_PATTERNS = [
        r'bot', r'crawl', r'spider', r'scrape',
        r'google', r'bing', r'yahoo', r'baidu',
        r'facebook', r'twitter', r'linkedin',
        r'wget', r'curl', r'python-requests'
    ]
    
    # Mobile user agents patterns
    MOBILE_PATTERNS = [
        r'mobile', r'android', r'iphone', r'ipad',
        r'blackberry', r'windows phone'
    ]
    
    # Paths to exclude from analytics
    EXCLUDED_PATHS = [
        r'/admin/',
        r'/static/',
        r'/media/',
        r'/favicon\.ico',
        r'/robots\.txt',
        r'/sitemap\.xml',
        r'/__debug__/',
    ]
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.compiled_bot_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.BOT_PATTERNS]
        self.compiled_mobile_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.MOBILE_PATTERNS]
        self.compiled_excluded_paths = [re.compile(pattern) for pattern in self.EXCLUDED_PATHS]
    
    def process_request(self, request):
        """Start timing the request."""
        request._analytics_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Track the request after response is generated."""
        
        # Skip if analytics is disabled
        if not getattr(settings, 'ENABLE_ANALYTICS', True):
            return response
        
        # Skip excluded paths
        if self.should_exclude_path(request.path):
            return response
        
        # Calculate response time
        start_time = getattr(request, '_analytics_start_time', None)
        response_time_ms = None
        if start_time:
            response_time_ms = int((time.time() - start_time) * 1000)
        
        # Collect analytics data
        analytics_data = self.collect_analytics_data(request, response, response_time_ms)
        
        # Save analytics data asynchronously
        try:
            self.save_analytics_data(analytics_data)
        except Exception as e:
            # Don't let analytics errors break the response
            if settings.DEBUG:
                print(f"Analytics error: {e}")
        
        return response
    
    def should_exclude_path(self, path):
        """Check if path should be excluded from analytics."""
        for pattern in self.compiled_excluded_paths:
            if pattern.search(path):
                return True
        return False
    
    def collect_analytics_data(self, request, response, response_time_ms):
        """Collect analytics data from request and response."""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return {
            'path': request.path[:500],  # Truncate long paths
            'method': request.method,
            'status_code': response.status_code,
            'ip_address': self.get_client_ip(request),
            'user_agent': user_agent[:1000],  # Truncate long user agents
            'referer': request.META.get('HTTP_REFERER', '')[:500],
            'timestamp': timezone.now(),
            'response_time_ms': response_time_ms,
            'session_key': request.session.session_key if hasattr(request, 'session') else '',
            'user': request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
            'is_bot': self.is_bot(user_agent),
            'is_mobile': self.is_mobile(user_agent),
        }
    
    def get_client_ip(self, request):
        """Get the client's real IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        # Handle IPv6 localhost
        if ip in ['::1', '127.0.0.1']:
            return '127.0.0.1'
        
        return ip[:45]  # IPv6 max length
    
    def is_bot(self, user_agent):
        """Check if request is from a bot."""
        for pattern in self.compiled_bot_patterns:
            if pattern.search(user_agent):
                return True
        return False
    
    def is_mobile(self, user_agent):
        """Check if request is from a mobile device."""
        for pattern in self.compiled_mobile_patterns:
            if pattern.search(user_agent):
                return True
        return False
    
    def save_analytics_data(self, data):
        """Save analytics data to database."""
        from .models import PageView, PopularPage
        from django.db.models import F
        
        # Use transaction to ensure data consistency
        with transaction.atomic():
            PageView.objects.create(**data)
            
            # Update popular pages
            self.update_popular_pages(data['path'], data['response_time_ms'])
    
    def update_popular_pages(self, path, response_time_ms):
        """Update popular pages statistics."""
        from .models import PopularPage
        from django.db.models import F
        
        popular_page, created = PopularPage.objects.get_or_create(
            path=path,
            defaults={'total_views': 1, 'unique_views': 1}
        )
        
        if not created:
            # Update counters
            popular_page.total_views = F('total_views') + 1
            
            # Update average response time
            if response_time_ms:
                if popular_page.avg_response_time:
                    # Calculate new average
                    popular_page.avg_response_time = (
                        (popular_page.avg_response_time + response_time_ms) / 2
                    )
                else:
                    popular_page.avg_response_time = response_time_ms
            
            popular_page.save(update_fields=['total_views', 'avg_response_time', 'last_viewed'])
