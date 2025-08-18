#!/usr/bin/env python3
"""
Test script to verify British date formatting in Django.
"""

import os
import sys
import django
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, '/workspaces/sk-com')

# Set up Django environment
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-key-for-date-format-testing')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')

# Initialize Django
django.setup()

from django.template import Template, Context
from django.utils import timezone, formats
from django.conf import settings

def test_date_formatting():
    """Test various date formatting options."""
    
    print("Django Settings:")
    print(f"LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
    print(f"TIME_ZONE: {settings.TIME_ZONE}")
    print(f"USE_I18N: {settings.USE_I18N}")
    print(f"USE_TZ: {settings.USE_TZ}")
    print(f"USE_L10N: {getattr(settings, 'USE_L10N', 'Not set')}")
    
    # Create a test date
    test_date = datetime(2025, 8, 18, 14, 30, 0)
    test_date_aware = timezone.make_aware(test_date)
    
    print(f"\nTest date: {test_date}")
    print(f"Test date (timezone aware): {test_date_aware}")
    
    # Test Django's date formatting
    print("\nDjango Date Formatting:")
    print(f"Default date format: {formats.date_format(test_date_aware)}")
    print(f"Short date format: {formats.date_format(test_date_aware, 'SHORT_DATE_FORMAT')}")
    
    # Test template date filters
    print("\nTemplate Date Filters:")
    template_tests = [
        ('{{ date|date }}', 'Default date filter'),
        ('{{ date|date:"d/m/Y" }}', 'British date format (d/m/Y)'),
        ('{{ date|date:"j M Y" }}', 'British date format (j M Y)'),
        ('{{ date|date:"M Y" }}', 'Month Year format'),
        ('{{ date|date:"F d, Y" }}', 'US format for comparison'),
    ]
    
    for template_str, description in template_tests:
        template = Template(template_str)
        context = Context({'date': test_date_aware})
        result = template.render(context)
        print(f"{description}: {result}")

if __name__ == '__main__':
    test_date_formatting()
