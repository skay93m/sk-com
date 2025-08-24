from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
import logging
import os

logger = logging.getLogger(__name__)


class SecureAdminLoginView(LoginView):
    """
    Custom login view that sets a secure session flag for admin access.
    """
    template_name = 'admin/login.html'
    
    def form_valid(self, form):
        try:
            # Set the secure admin access flag in session
            self.request.session['secure_admin_access'] = True
            response = super().form_valid(form)
            
            # Redirect to admin or the 'next' parameter
            next_url = self.request.GET.get('next', '/admin/')
            return redirect(next_url)
        except Exception as e:
            logger.error(f"Error in SecureAdminLoginView.form_valid: {e}")
            messages.error(self.request, 'Login failed. Please try again.')
            return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Secure Admin Login'
        context['site_header'] = 'Secure Admin Access'
        return context


class SecureAdminLogoutView(View):
    """
    Custom logout view that clears the secure session flag.
    """
    
    def get(self, request):
        # Clear the secure admin access flag
        if 'secure_admin_access' in request.session:
            del request.session['secure_admin_access']
        
        # Redirect to Django's admin logout
        return redirect('/admin/logout/')


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
