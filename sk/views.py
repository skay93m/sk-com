from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import os

@method_decorator(cache_control(max_age=86400), name='dispatch')  # Cache for 24 hours
class RobotsTxtView(View):
    """
    Serve robots.txt file with proper content type and caching.
    """
    
    def get(self, request):
        from django.conf import settings
        
        # Try project root first, then static directory
        robots_paths = [
            os.path.join(settings.BASE_DIR, 'robots.txt'),
            os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'robots.txt') if settings.STATIC_ROOT or settings.STATICFILES_DIRS else None
        ]
        
        content = None
        for robots_path in robots_paths:
            if robots_path and os.path.exists(robots_path):
                try:
                    with open(robots_path, 'r') as f:
                        content = f.read()
                        break
                except FileNotFoundError:
                    continue
        
        if not content:
            # Fallback robots.txt content if file not found
            content = """User-agent: *
Disallow: /admin/
Disallow: /secure-admin-login/
Disallow: /*.php
Disallow: /*.asp
Disallow: /*.aspx
Crawl-delay: 1
"""
        
        return HttpResponse(content, content_type='text/plain')
