#!/usr/bin/env python3
"""
Test credential creation via HTTP request
"""
import os
import sys
import django

# Setup Django before importing models
sys.path.insert(0, '/workspaces/sk-com')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Add the project directory to the Python path

# Setup Django

def test_credential_creation():
    """Test credential creation via Django test client"""
    print("Testing credential creation via HTTP...")
    
    # Create a test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        user.is_staff = True
        user.save()
        print("✓ Created test user")
    
    # Create Django test client
    client = Client()
    
    # Login the user
    client.login(username='testuser', password='testpass')
    print("✓ Logged in test user")
    
    # Test GET request to credential form
    print("\n1. Testing GET request to credential form:")
    response = client.get('/cv/credential/new/')
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Form page loads successfully")
        if b'Add a new credential' in response.content:
            print("   ✓ Form contains expected content")
    
    # Test POST with invalid data (missing fields)
    print("\n2. Testing POST with invalid data:")
    response = client.post('/cv/credential/new/', {
        'title': '',  # Empty title
        'institution': 'Test Institution',
        'date_obtained': '2025-01-01',
        'link': 'https://example.com'
        # Missing icon
    })
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:  # Should stay on form page due to validation errors
        print("   ✓ Form correctly rejected invalid data")
        if b'This field is required' in response.content or b'Please either select an existing icon' in response.content:
            print("   ✓ Error messages displayed correctly")
    
    # Test POST with valid data
    print("\n3. Testing POST with valid data:")
    response = client.post('/cv/credential/new/', {
        'title': 'Test Credential',
        'institution': 'Test Institution',
        'date_obtained': '2025-01-01',
        'link': 'https://example.com',
        'icon_choice': 'graduation.png'
    })
    print(f"   Status code: {response.status_code}")
    if response.status_code == 302:  # Should redirect after successful creation
        print("   ✓ Successfully created credential (redirected)")
        print(f"   Redirect URL: {response.url}")
    else:
        print(f"   ✗ Unexpected status code. Response content: {response.content[:500]}")
    
    # Test checking if credential was actually created
    print("\n4. Checking if credential was created:")
    from cv.models import Credentials
    credentials = Credentials.objects.filter(title='Test Credential')
    if credentials.exists():
        credential = credentials.first()
        print(f"   ✓ Credential created with ID: {credential.pk}")
        print(f"   Title: {credential.title}")
        print(f"   Institution: {credential.institution}")
        print(f"   Icon: {credential.icon}")
        
        # Test redirect to detail page
        detail_response = client.get(f'/cv/credential/{credential.pk}')
        print(f"   Detail page status: {detail_response.status_code}")
        if detail_response.status_code == 200:
            print("   ✓ Detail page accessible")
    else:
        print("   ✗ Credential was not created")

if __name__ == '__main__':
    test_credential_creation()
    print("\n✓ All tests completed!")
