#!/usr/bin/env python
"""
Production Configuration Validator

Run this script to validate your production settings before deployment.
Usage: python scripts/validate_production.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')

try:
    import django
    django.setup()
    
    from django.conf import settings
    from django.core.management import execute_from_command_line
    from django.core.exceptions import ImproperlyConfigured
    
    def validate_production_settings():
        """Validate critical production settings."""
        issues = []
        warnings = []
        
        # Critical security checks
        if settings.DEBUG:
            issues.append("❌ DEBUG is True - MUST be False in production")
        else:
            print("✅ DEBUG is False")
        
        if settings.SECRET_KEY == 'your-development-secret-key-here-change-in-production':
            issues.append("❌ SECRET_KEY is still using development value")
        elif len(settings.SECRET_KEY) < 50:
            warnings.append("⚠️  SECRET_KEY should be longer (50+ characters)")
        else:
            print("✅ SECRET_KEY is configured")
        
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            issues.append("❌ ALLOWED_HOSTS not properly configured")
        else:
            print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # HTTPS/SSL checks
        if not settings.DEBUG:
            if not settings.SECURE_SSL_REDIRECT:
                warnings.append("⚠️  SECURE_SSL_REDIRECT should be True in production")
            else:
                print("✅ SSL redirect enabled")
            
            if not settings.CSRF_COOKIE_SECURE:
                warnings.append("⚠️  CSRF_COOKIE_SECURE should be True in production")
            else:
                print("✅ CSRF cookies secured")
            
            if not settings.SESSION_COOKIE_SECURE:
                warnings.append("⚠️  SESSION_COOKIE_SECURE should be True in production")
            else:
                print("✅ Session cookies secured")
        
        # Database checks
        db_config = settings.DATABASES['default']
        if db_config['ENGINE'] == 'django.db.backends.sqlite3' and not settings.DEBUG:
            warnings.append("⚠️  Using SQLite in production - consider PostgreSQL")
        elif db_config['ENGINE'] == 'django.db.backends.postgresql':
            print("✅ PostgreSQL configured")
        
        # CSRF trusted origins
        if not settings.CSRF_TRUSTED_ORIGINS:
            issues.append("❌ CSRF_TRUSTED_ORIGINS is empty")
        else:
            print(f"✅ CSRF trusted origins: {settings.CSRF_TRUSTED_ORIGINS}")
        
        # Static files
        if not os.path.exists(settings.STATIC_ROOT):
            warnings.append("⚠️  STATIC_ROOT directory doesn't exist - run collectstatic")
        else:
            print("✅ Static files directory exists")
        
        return issues, warnings
    
    def main():
        print("🔍 Validating Production Configuration...")
        print("=" * 50)
        
        try:
            issues, warnings = validate_production_settings()
            
            print("\n📋 Validation Results:")
            print("=" * 50)
            
            if issues:
                print("\n🚨 CRITICAL ISSUES (must fix before production):")
                for issue in issues:
                    print(f"  {issue}")
            
            if warnings:
                print("\n⚠️  WARNINGS (recommended to fix):")
                for warning in warnings:
                    print(f"  {warning}")
            
            if not issues and not warnings:
                print("\n🎉 All checks passed! Configuration looks good for production.")
            elif not issues:
                print("\n✅ No critical issues found. Review warnings above.")
            else:
                print(f"\n❌ Found {len(issues)} critical issue(s) that must be fixed.")
                return 1
            
            return 0
            
        except Exception as e:
            print(f"\n❌ Error during validation: {e}")
            return 1
    
    if __name__ == "__main__":
        sys.exit(main())
        
except ImportError as e:
    print(f"Error importing Django: {e}")
    print("Make sure you're in the project directory and Django is installed.")
    sys.exit(1)
