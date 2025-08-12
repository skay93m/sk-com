from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Quick database health check command'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Running Database Health Check...\n')
        )

        # Test 1: Basic connection
        try:
            user_count = User.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Database connected - Found {user_count} users')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database connection failed: {e}')
            )
            return

        # Test 2: Create operation
        try:
            test_user = User.objects.create_user(
                username='health_check_user',
                email='healthcheck@example.com',
                password='temppassword123'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✅ CREATE test passed - User ID: {test_user.id}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ CREATE test failed: {e}')
            )
            return

        # Test 3: Read operation
        try:
            user = User.objects.get(username='health_check_user')
            self.stdout.write(
                self.style.SUCCESS(f'✅ READ test passed - Found: {user.username}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ READ test failed: {e}')
            )
            return

        # Test 4: Update operation
        try:
            user.first_name = 'Health'
            user.last_name = 'Check'
            user.save()
            updated_user = User.objects.get(username='health_check_user')
            self.stdout.write(
                self.style.SUCCESS(f'✅ UPDATE test passed - Name: {updated_user.get_full_name()}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ UPDATE test failed: {e}')
            )
            return

        # Test 5: Delete operation
        try:
            user.delete()
            try:
                User.objects.get(username='health_check_user')
                self.stdout.write(
                    self.style.ERROR('❌ DELETE test failed - User still exists')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.SUCCESS('✅ DELETE test passed - User removed')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ DELETE test failed: {e}')
            )
            return

        # Test 6: Transaction test
        try:
            with transaction.atomic():
                test_user = User.objects.create_user(
                    username='transaction_test_user',
                    email='transaction@example.com',
                    password='temppassword123'
                )
                # Simulate an error to trigger rollback
                raise Exception("Intentional rollback")
        except Exception:
            # Check if rollback worked
            try:
                User.objects.get(username='transaction_test_user')
                self.stdout.write(
                    self.style.ERROR('❌ TRANSACTION test failed - Rollback did not work')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.SUCCESS('✅ TRANSACTION test passed - Rollback worked')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 All database tests completed successfully!')
        )
