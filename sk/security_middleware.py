"""
Security middleware for detecting and logging suspicious requests.
"""
import logging
import re
from django.http import HttpResponseNotFound
from django.conf import settings

logger = logging.getLogger('security')

class SecurityMiddleware:
    """
    Middleware to detect and handle suspicious requests.
    """
    
    # Common malicious file extensions and paths
    SUSPICIOUS_PATTERNS = [
        r'\.php$',
        r'\.asp$',
        r'\.aspx$',
        r'\.jsp$',
        r'\.cgi$',
        r'/wp-admin/',
        r'/wp-content/',
        r'/wp-includes/',
        r'/phpmyadmin/',
        r'/cpanel/',
        r'/cgi-bin/',
        r'/\.env',
        r'/\.git/',
        r'\.sql$',
        r'\.db$',
        r'\.backup$',
        r'\.bak$',
        r'/config\.php',
        r'/admin\.php',
        r'/login\.php',
        r'/xmlrpc\.php',
    ]
    
    # Compile patterns for better performance
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if the request path matches suspicious patterns
        if self.is_suspicious_request(request):
            self.log_suspicious_request(request)
            
            # Optionally return 404 instead of processing the request
            # This makes it appear as if the file doesn't exist
            if getattr(settings, 'BLOCK_SUSPICIOUS_REQUESTS', True):
                return HttpResponseNotFound()
        
        response = self.get_response(request)
        return response
    
    def is_suspicious_request(self, request):
        """
        Check if the request path matches any suspicious patterns.
        """
        path = request.path
        
        for pattern in self.compiled_patterns:
            if pattern.search(path):
                return True
        
        return False
    
    def log_suspicious_request(self, request):
        """
        Log suspicious requests with client information.
        """
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        logger.warning(
            f"Suspicious request detected: "
            f"IP={client_ip}, "
            f"Path={request.path}, "
            f"Method={request.method}, "
            f"User-Agent={user_agent}"
        )
    
    def get_client_ip(self, request):
        """
        Get the client's real IP address.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
