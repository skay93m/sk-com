#!/usr/bin/env python3
"""
Database setup and check script for sk-website project.
This script helps with PostgreSQL setup and checks which database is being used.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sk.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.core.management import execute_from_command_line
    from django.db import connection
except ImportError as e:
    print(f"Error importing Django: {e}")
    print("Make sure you have installed the dependencies with: uv sync")
    sys.exit(1)


def check_postgresql_service():
    """Check if PostgreSQL service is running."""
    try:
        # Try connecting to PostgreSQL directly
        result = subprocess.run(['pg_isready', '-h', 'localhost'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_database_connection():
    """Check current database connection and return database info."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        db_config = settings.DATABASES['default']
        return {
            'success': True,
            'engine': db_config['ENGINE'],
            'name': db_config.get('NAME', 'N/A'),
            'host': db_config.get('HOST', 'N/A'),
            'port': db_config.get('PORT', 'N/A'),
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'engine': settings.DATABASES['default']['ENGINE'],
        }


def create_postgresql_database():
    """Create PostgreSQL database if it doesn't exist."""
    db_name = os.environ.get('DB_NAME', 'sk_website')
    db_user = os.environ.get('DB_USER', 'postgres')
    
    print(f"Creating PostgreSQL database '{db_name}'...")
    
    try:
        # Create database
        subprocess.run([
            'sudo', '-u', 'postgres', 'createdb', db_name
        ], check=True, capture_output=True)
        print(f"✅ Database '{db_name}' created successfully!")
        
        # Grant privileges to user
        subprocess.run([
            'sudo', '-u', 'postgres', 'psql', '-c',
            f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        ], check=True, capture_output=True)
        print(f"✅ Privileges granted to user '{db_user}'!")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating database: {e}")
        return False


def main():
    """Main function to check and setup database."""
    print("🔍 SK-Website Database Setup & Check")
    print("=" * 40)
    
    # Check PostgreSQL service
    print("1. Checking PostgreSQL service...")
    pg_running = check_postgresql_service()
    if pg_running:
        print("✅ PostgreSQL service is running")
    else:
        print("❌ PostgreSQL service is not running or not installed")
        print("   Install PostgreSQL or the app will use SQLite fallback")
    
    # Check database connection
    print("\n2. Checking database connection...")
    db_info = check_database_connection()
    
    if db_info['success']:
        engine = db_info['engine'].split('.')[-1]  # Get last part (postgresql/sqlite3)
        print(f"✅ Connected to {engine.upper()} database")
        print(f"   Database: {db_info['name']}")
        if 'host' in db_info and db_info['host'] != 'N/A':
            print(f"   Host: {db_info['host']}:{db_info['port']}")
    else:
        engine = db_info['engine'].split('.')[-1]
        print(f"❌ Failed to connect to {engine.upper()} database")
        print(f"   Error: {db_info['error']}")
        
        if 'postgresql' in db_info['engine'] and pg_running:
            print("\n🔧 Attempting to create PostgreSQL database...")
            if create_postgresql_database():
                print("   Try running this script again!")
            else:
                print("   Manual database creation may be needed.")
    
    # Check migrations
    print("\n3. Checking migrations...")
    try:
        from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
        from io import StringIO
        from django.core.management.base import CommandError
        
        # Capture showmigrations output
        output = StringIO()
        command = ShowMigrationsCommand()
        command.stdout = output
        command.handle(verbosity=0)
        
        migrations_output = output.getvalue()
        if migrations_output.strip():
            unapplied = [line for line in migrations_output.split('\n') if '[ ]' in line]
            if unapplied:
                print(f"⚠️  Found {len(unapplied)} unapplied migrations")
                print("   Run: python manage.py migrate")
            else:
                print("✅ All migrations are applied")
        else:
            print("✅ No migrations needed")
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
    
    # Summary
    print("\n📋 Summary:")
    if db_info['success']:
        engine = db_info['engine'].split('.')[-1].upper()
        print(f"✅ Your app is using {engine} database")
        if engine == 'SQLITE3':
            print("   Consider setting up PostgreSQL for consistency with production")
        else:
            print("   PostgreSQL setup is complete!")
    else:
        print("❌ Database connection failed")
        print("   The app will try PostgreSQL first, then fall back to SQLite")
    
    print("\n🚀 Next steps:")
    print("   1. Run migrations: python manage.py migrate")
    print("   2. Create superuser: python manage.py createsuperuser")
    print("   3. Start development: python manage.py runserver")


if __name__ == '__main__':
    main()
