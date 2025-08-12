from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Check database connectivity and configuration'

    def handle(self, *args, **options):
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            self.stdout.write(
                self.style.SUCCESS('Database connection successful!')
            )
            
            # Print database config (without sensitive info)
            db_config = settings.DATABASES['default']
            self.stdout.write(f"Database Engine: {db_config['ENGINE']}")
            self.stdout.write(f"Database Name: {db_config['NAME']}")
            self.stdout.write(f"Database Host: {db_config['HOST']}")
            self.stdout.write(f"Database Port: {db_config['PORT']}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database connection failed: {str(e)}')
            )
            return False
