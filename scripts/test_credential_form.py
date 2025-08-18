#!/usr/bin/env python3
"""
Test script to verify credential form functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, '/workspaces/sk-com')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')
django.setup()

from cv.forms import CredentialForm
from cv.models import Credentials
from django.contrib.auth.models import User
from django.test import RequestFactory
from cv.views import credential_create
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

def test_form_validation():
    """Test form validation scenarios"""
    print("Testing credential form validation...")
    
    # Test empty form
    print("\n1. Testing empty form submission:")
    form = CredentialForm({})
    if not form.is_valid():
        print("✓ Empty form correctly identified as invalid")
        print(f"   Errors: {form.errors}")
    else:
        print("✗ Empty form incorrectly passed validation")
    
    # Test form without icon
    print("\n2. Testing form without icon:")
    form = CredentialForm({
        'title': 'Test Credential',
        'institution': 'Test Institution',
        'date_obtained': '2025-01-01',
        'link': 'https://example.com'
    })
    if not form.is_valid():
        print("✓ Form without icon correctly identified as invalid")
        print(f"   Errors: {form.errors}")
    else:
        print("✗ Form without icon incorrectly passed validation")
    
    # Test valid form with icon choice
    print("\n3. Testing valid form with icon choice:")
    form = CredentialForm({
        'title': 'Test Credential',
        'institution': 'Test Institution',
        'date_obtained': '2025-01-01',
        'link': 'https://example.com',
        'icon_choice': 'graduation.png'
    })
    if form.is_valid():
        print("✓ Valid form with icon choice correctly passed validation")
    else:
        print("✗ Valid form with icon choice incorrectly failed validation")
        print(f"   Errors: {form.errors}")

def test_view_with_errors():
    """Test view error handling"""
    print("\n\nTesting view error handling...")
    
    # Create a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        user.is_staff = True
        user.save()
    
    # Create a request factory
    factory = RequestFactory()
    
    # Test POST with invalid data
    print("\n1. Testing POST with invalid data:")
    request = factory.post('/cv/credential/new/', {
        'title': '',  # Empty title
        'institution': 'Test Institution',
        'date_obtained': '2025-01-01',
        'link': 'https://example.com'
        # Missing icon
    })
    request.user = user
    
    # Add session and messages to request
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    
    messages = FallbackStorage(request)
    request._messages = messages
    
    response = credential_create(request)
    print(f"   Response status: {response.status_code}")
    
    # Check if messages were added
    storage = messages._get()[0]
    if storage:
        print(f"   Messages added: {[str(msg) for msg in storage]}")
    else:
        print("   No messages added")

if __name__ == '__main__':
    test_form_validation()
    test_view_with_errors()
    print("\n✓ All tests completed!")
