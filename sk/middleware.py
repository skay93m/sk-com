from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)


class SecureAdminMiddleware:
    """
    Middleware to secure admin access by requiring a special session flag
    that is only set when accessing admin through the authorized login button.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Check if accessing admin URLs
            if request.path.startswith('/admin/'):
                # Allow login page and logout
                if request.path in ['/admin/login/', '/admin/logout/']:
                    response = self.get_response(request)
                    return response
                
                # Check if user is authenticated and has the secure access flag
                if not request.user.is_authenticated:
                    return redirect('secure_admin_login')
                
                # Check for secure access flag in session
                if not request.session.get('secure_admin_access', False):
                    # Try to add message, but handle gracefully if messages middleware isn't available
                    try:
                        messages.error(request, 'Access denied. Please use the authorized login method.')
                    except Exception as msg_error:
                        logger.warning(f"Could not add message: {msg_error}")
                    return redirect('home')  # Redirect to home page
            
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Error in SecureAdminMiddleware: {e}")
            # If there's an error in the middleware, redirect to secure login
            if request.path.startswith('/admin/'):
                return redirect('secure_admin_login')
            # Otherwise, let the error propagate
            raise
