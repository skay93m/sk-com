#!/usr/bin/env python
"""
Database CRUD Operations Test Script
This script tests Create, Read, Update, Delete operations on the database.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth.models import User
from django.core.management.color import make_style

style = make_style()

def test_database_connection():
    """Test basic database connection"""
    print(style.HTTP_INFO("🔍 Testing database connection..."))
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print(style.SUCCESS("✅ Database connection successful"))
                return True
    except Exception as e:
        print(style.ERROR(f"❌ Database connection failed: {e}"))
        return False

def get_database_info():
    """Get database configuration info"""
    print(style.HTTP_INFO("🔍 Database Configuration:"))
    db_config = connection.settings_dict
    print(f"  Engine: {db_config['ENGINE']}")
    print(f"  Name: {db_config['NAME']}")
    if db_config['ENGINE'] != 'django.db.backends.sqlite3':
        print(f"  Host: {db_config.get('HOST', 'localhost')}")
        print(f"  Port: {db_config.get('PORT', '5432')}")
        print(f"  User: {db_config.get('USER', 'N/A')}")

def test_create_operation():
    """Test CREATE operation"""
    print(style.HTTP_INFO("🔍 Testing CREATE operation..."))
    try:
        # Create a test user
        test_user = User.objects.create_user(
            username='test_crud_user',
            email='test@example.com',
            password='testpassword123'
        )
        print(style.SUCCESS(f"✅ CREATE successful - User created with ID: {test_user.id}"))
        return test_user
    except Exception as e:
        print(style.ERROR(f"❌ CREATE failed: {e}"))
        return None

def test_read_operation(user_id):
    """Test READ operation"""
    print(style.HTTP_INFO("🔍 Testing READ operation..."))
    try:
        # Read the user we just created
        user = User.objects.get(id=user_id)
        print(style.SUCCESS(f"✅ READ successful - Found user: {user.username} ({user.email})"))
        
        # Test query operations
        user_count = User.objects.count()
        print(style.SUCCESS(f"✅ Total users in database: {user_count}"))
        return True
    except Exception as e:
        print(style.ERROR(f"❌ READ failed: {e}"))
        return False

def test_update_operation(user_id):
    """Test UPDATE operation"""
    print(style.HTTP_INFO("🔍 Testing UPDATE operation..."))
    try:
        # Update the user
        user = User.objects.get(id=user_id)
        original_email = user.email
        user.email = 'updated_test@example.com'
        user.first_name = 'Test'
        user.last_name = 'User'
        user.save()
        
        # Verify the update
        updated_user = User.objects.get(id=user_id)
        if updated_user.email == 'updated_test@example.com':
            print(style.SUCCESS(f"✅ UPDATE successful - Email changed from {original_email} to {updated_user.email}"))
            return True
        else:
            print(style.ERROR("❌ UPDATE failed - Changes not saved"))
            return False
    except Exception as e:
        print(style.ERROR(f"❌ UPDATE failed: {e}"))
        return False

def test_delete_operation(user_id):
    """Test DELETE operation"""
    print(style.HTTP_INFO("🔍 Testing DELETE operation..."))
    try:
        # Delete the user
        user = User.objects.get(id=user_id)
        username = user.username
        user.delete()
        
        # Verify deletion
        try:
            User.objects.get(id=user_id)
            print(style.ERROR("❌ DELETE failed - User still exists"))
            return False
        except User.DoesNotExist:
            print(style.SUCCESS(f"✅ DELETE successful - User '{username}' removed"))
            return True
    except Exception as e:
        print(style.ERROR(f"❌ DELETE failed: {e}"))
        return False

def test_transaction_rollback():
    """Test transaction handling"""
    print(style.HTTP_INFO("🔍 Testing transaction rollback..."))
    try:
        with transaction.atomic():
            # Create a user
            test_user = User.objects.create_user(
                username='rollback_test_user',
                email='rollback@example.com',
                password='testpassword123'
            )
            user_id = test_user.id
            
            # Intentionally cause an error to trigger rollback
            raise Exception("Intentional rollback test")
            
    except Exception:
        # Check if user was rolled back
        try:
            User.objects.get(id=user_id)
            print(style.ERROR("❌ Transaction rollback failed - User still exists"))
            return False
        except User.DoesNotExist:
            print(style.SUCCESS("✅ Transaction rollback successful"))
            return True
    except Exception as e:
        print(style.ERROR(f"❌ Transaction test failed: {e}"))
        return False

def run_comprehensive_test():
    """Run all database tests"""
    print(style.HTTP_SUCCESS("🚀 Starting Comprehensive Database CRUD Test\n"))
    
    # Get database info
    get_database_info()
    print()
    
    # Test connection
    if not test_database_connection():
        return False
    print()
    
    # Test CRUD operations
    test_user = test_create_operation()
    if not test_user:
        return False
    print()
    
    if not test_read_operation(test_user.id):
        return False
    print()
    
    if not test_update_operation(test_user.id):
        return False
    print()
    
    if not test_delete_operation(test_user.id):
        return False
    print()
    
    # Test transaction handling
    if not test_transaction_rollback():
        return False
    print()
    
    print(style.HTTP_SUCCESS("🎉 All database tests passed! Your database is working correctly."))
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
