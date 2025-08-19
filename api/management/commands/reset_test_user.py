from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset the test user password and ensure proper setup'

    def handle(self, *args, **options):
        email = 'test@example.com'
        password = 'testpass123'
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
                'user_type': 'designer',
                'password': make_password(password)
            }
        )
        
        if not created:
            # Update existing user
            user.first_name = 'Test'
            user.last_name = 'User'
            user.is_active = True
            user.user_type = 'designer'
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated test user: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created test user: {email}'))
        
        # Verify the password was set correctly
        user.refresh_from_db()
        if user.check_password(password):
            self.stdout.write(self.style.SUCCESS('Password verified!'))
        else:
            self.stdout.write(self.style.ERROR('Password verification failed!'))
        
        # Print login instructions
        self.stdout.write(self.style.SUCCESS('\nTest User Credentials:'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS('\nTest login with:'))
        self.stdout.write(self.style.SUCCESS(f'curl -X POST http://127.0.0.1:8001/api/v1/token/ -H "Content-Type: application/json" -d \'{{"email":"{email}", "password":"{password}"}}\''))
