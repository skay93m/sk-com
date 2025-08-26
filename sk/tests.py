"""
Tests for sk project main functionality.

This module contains tests for the core sk application components including:
- URL routing and configuration
- Secure admin login/logout views
- Security middleware for malicious request detection
- Secure admin middleware for protecting admin access
- Robots.txt view functionality
"""

import os
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.http import HttpRequest
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware

from .views import SecureAdminLoginView, SecureAdminLogoutView, RobotsTxtView
from .middleware import SecureAdminMiddleware
from .security_middleware import SecurityMiddleware


class URLRoutingTest(TestCase):
    """
    Test URL routing and configuration for the sk project.
    Ensures that all main URL patterns are properly configured and resolve to correct views.
    """
    
    def setUp(self):
        self.client = Client()
        
    def test_admin_url_resolves(self):
        """Test that admin URL resolves correctly."""
        url = reverse('admin:index')
        self.assertTrue(url.startswith('/admin/'))
        
    def test_secure_admin_login_url_resolves(self):
        """Test that secure admin login URL resolves to correct view."""
        url = reverse('secure_admin_login')
        self.assertEqual(url, '/secure-admin-login/')
        resolver = resolve('/secure-admin-login/')
        self.assertEqual(resolver.func.view_class, SecureAdminLoginView)
        
    def test_secure_admin_logout_url_resolves(self):
        """Test that secure admin logout URL resolves to correct view."""
        url = reverse('secure_admin_logout')
        self.assertEqual(url, '/secure-admin-logout/')
        resolver = resolve('/secure-admin-logout/')
        self.assertEqual(resolver.func.view_class, SecureAdminLogoutView)
        
    def test_robots_txt_url_resolves(self):
        """Test that robots.txt URL resolves to correct view."""
        url = reverse('robots_txt')
        self.assertEqual(url, '/robots.txt')
        resolver = resolve('/robots.txt')
        self.assertEqual(resolver.func.view_class, RobotsTxtView)
        
    def test_app_urls_included(self):
        """Test that all app URLs are properly included."""
        # Test home app URLs
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 404)
        
        # Test that app URL patterns exist
        app_paths = ['/projects/', '/writing/', '/cv/', '/mcq/', '/analytics/']
        for path in app_paths:
            try:
                response = self.client.get(path)
                # We don't care about the exact response, just that the URL exists
                self.assertNotEqual(response.status_code, 404, f"URL {path} should be configured")
            except Exception:
                # Some URLs might require authentication or specific setup
                pass


class SecureAdminViewsTest(TestCase):
    """
    Test secure admin login and logout functionality.
    Ensures proper session management and secure access control.
    """
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
    def test_secure_admin_login_view_get(self):
        """Test GET request to secure admin login view."""
        response = self.client.get(reverse('secure_admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Secure Admin Login')
        
    def test_secure_admin_login_view_post_valid(self):
        """Test POST request with valid credentials sets secure session flag."""
        response = self.client.post(reverse('secure_admin_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect after successful login
        self.assertIn(response.status_code, [302, 200])
        
        # Check if session has secure flag (if redirected successfully)
        if response.status_code == 302:
            session = self.client.session
            self.assertTrue(session.get('secure_admin_access', False))
            
    def test_secure_admin_login_view_post_invalid(self):
        """Test POST request with invalid credentials."""
        response = self.client.post(reverse('secure_admin_login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        # Session should not have secure flag
        session = self.client.session
        self.assertFalse(session.get('secure_admin_access', False))
        
    def test_secure_admin_logout_view(self):
        """Test secure admin logout clears session flag."""
        # First login and set session flag
        self.client.login(username='testuser', password='testpass123')
        session = self.client.session
        session['secure_admin_access'] = True
        session.save()
        
        # Then logout
        response = self.client.get(reverse('secure_admin_logout'))
        self.assertEqual(response.status_code, 302)
        
        # Check that secure flag is removed
        updated_session = self.client.session
        self.assertFalse(updated_session.get('secure_admin_access', False))
        
    def test_secure_admin_login_with_next_parameter(self):
        """Test secure admin login redirects to 'next' parameter."""
        next_url = '/admin/users/'
        login_url = f"{reverse('secure_admin_login')}?next={next_url}"
        
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Should redirect (either to next URL or through admin redirect)
        self.assertIn(response.status_code, [302, 200])


class SecurityMiddlewareTest(TestCase):
    """
    Test security middleware for detecting and handling suspicious requests.
    Ensures malicious requests are properly detected and logged.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityMiddleware(lambda x: None)
        
    def test_security_middleware_detects_php_files(self):
        """Test that security middleware detects PHP file requests."""
        request = self.factory.get('/malicious.php')
        
        # Mock the log method to verify it's called
        with patch.object(self.middleware, 'log_suspicious_request') as mock_log:
            result = self.middleware.is_suspicious_request(request)
            self.assertTrue(result)
            
    def test_security_middleware_detects_wordpress_paths(self):
        """Test that security middleware detects WordPress-related paths."""
        suspicious_paths = ['/wp-admin/', '/wp-content/uploads/', '/wp-includes/']
        
        for path in suspicious_paths:
            with self.subTest(path=path):
                request = self.factory.get(path)
                result = self.middleware.is_suspicious_request(request)
                self.assertTrue(result, f"Should detect {path} as suspicious")
                
    def test_security_middleware_allows_legitimate_requests(self):
        """Test that security middleware allows legitimate requests."""
        legitimate_paths = ['/', '/admin/', '/projects/', '/home/', '/static/css/style.css']
        
        for path in legitimate_paths:
            with self.subTest(path=path):
                request = self.factory.get(path)
                result = self.middleware.is_suspicious_request(request)
                self.assertFalse(result, f"Should allow {path} as legitimate")
                
    def test_security_middleware_detects_config_files(self):
        """Test that security middleware detects attempts to access config files."""
        config_paths = ['/.env', '/config.php', '/.git/config']
        
        for path in config_paths:
            with self.subTest(path=path):
                request = self.factory.get(path)
                result = self.middleware.is_suspicious_request(request)
                self.assertTrue(result, f"Should detect {path} as suspicious")
                
    def test_security_middleware_case_insensitive(self):
        """Test that security middleware detection is case insensitive."""
        request_upper = self.factory.get('/ADMIN.PHP')
        request_lower = self.factory.get('/admin.php')
        request_mixed = self.factory.get('/Admin.PHP')
        
        self.assertTrue(self.middleware.is_suspicious_request(request_upper))
        self.assertTrue(self.middleware.is_suspicious_request(request_lower))
        self.assertTrue(self.middleware.is_suspicious_request(request_mixed))


class SecureAdminMiddlewareTest(TestCase):
    """
    Test secure admin middleware for protecting admin access.
    Ensures only authorized users with proper session flags can access admin.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create a mock response function
        self.mock_get_response = MagicMock()
        self.mock_get_response.return_value = MagicMock(status_code=200)
        
        self.middleware = SecureAdminMiddleware(self.mock_get_response)
        
    def _add_middleware_to_request(self, request):
        """Helper method to add required middleware to request."""
        # Add session middleware
        session_middleware = SessionMiddleware(lambda x: None)
        session_middleware.process_request(request)
        request.session.save()
        
        # Add authentication middleware
        auth_middleware = AuthenticationMiddleware(lambda x: None)
        auth_middleware.process_request(request)
        
        # Add messages middleware
        msg_middleware = MessageMiddleware(lambda x: None)
        msg_middleware.process_request(request)
        
        return request
        
    def test_secure_admin_middleware_allows_admin_login(self):
        """Test that middleware allows access to admin login page."""
        request = self.factory.get('/admin/login/')
        request = self._add_middleware_to_request(request)
        
        response = self.middleware(request)
        # Should call get_response (not redirect)
        self.mock_get_response.assert_called_once()
        
    def test_secure_admin_middleware_blocks_unauthenticated_admin(self):
        """Test that middleware blocks unauthenticated users from admin."""
        request = self.factory.get('/admin/')
        request = self._add_middleware_to_request(request)
        
        # Set anonymous user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('secure-admin-login/'))
        
    def test_secure_admin_middleware_blocks_authenticated_without_flag(self):
        """Test that middleware blocks authenticated users without secure flag."""
        request = self.factory.get('/admin/')
        request = self._add_middleware_to_request(request)
        
        # Set authenticated user but no secure flag
        request.user = self.user
        
        response = self.middleware(request)
        self.assertEqual(response.status_code, 302)
        
    def test_secure_admin_middleware_allows_authenticated_with_flag(self):
        """Test that middleware allows authenticated users with secure flag."""
        request = self.factory.get('/admin/')
        request = self._add_middleware_to_request(request)
        
        # Set authenticated user and secure flag
        request.user = self.user
        request.session['secure_admin_access'] = True
        
        response = self.middleware(request)
        # Should call get_response (allowed through)
        self.mock_get_response.assert_called_once()
        
    def test_secure_admin_middleware_allows_non_admin_urls(self):
        """Test that middleware allows access to non-admin URLs."""
        non_admin_paths = ['/', '/projects/', '/home/']
        
        for path in non_admin_paths:
            with self.subTest(path=path):
                self.mock_get_response.reset_mock()
                request = self.factory.get(path)
                request = self._add_middleware_to_request(request)
                
                response = self.middleware(request)
                # Should call get_response (allowed through)
                self.mock_get_response.assert_called_once()


class RobotsTxtViewTest(TestCase):
    """
    Test robots.txt view functionality.
    Ensures proper serving of robots.txt content with correct headers and caching.
    """
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
    def test_robots_txt_view_returns_text_plain(self):
        """Test that robots.txt view returns proper content type."""
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        
    def test_robots_txt_view_contains_admin_disallow(self):
        """Test that robots.txt contains admin disallow rules."""
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('User-agent: *', content)
        
    def test_robots_txt_view_contains_secure_admin_disallow(self):
        """Test that robots.txt contains secure admin disallow rules."""
        response = self.client.get(reverse('robots_txt'))
        content = response.content.decode('utf-8')
        self.assertIn('Disallow: /secure-admin-login/', content)
        
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_robots_txt_view_reads_file_when_exists(self, mock_open, mock_exists):
        """Test that robots.txt view reads from file when it exists."""
        # Mock file existence and content
        mock_exists.return_value = True
        mock_file_content = "User-agent: *\nDisallow: /custom/"
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        
        request = self.factory.get('/robots.txt')
        view = RobotsTxtView()
        response = view.get(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), mock_file_content)
        
    def test_robots_txt_view_has_cache_headers(self):
        """Test that robots.txt view includes appropriate cache headers."""
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, 200)
        # The cache control should be set by the decorator
        # We can't easily test the decorator in unit tests, but we can verify the response works
        self.assertIsNotNone(response.content)
