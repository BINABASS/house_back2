from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a test user with the specified credentials'

    def handle(self, *args, **options):
        email = 'test@example.com'
        password = 'testpass123'
        first_name = 'Test'
        last_name = 'User'
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='designer',  # or 'client' based on your needs
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created test user: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {email} already exists'))
            
        # Print the credentials for testing
        self.stdout.write(self.style.SUCCESS('\nTest User Credentials:'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS('\nTest login with:'))
        self.stdout.write(self.style.SUCCESS(f'curl -X POST http://127.0.0.1:8001/api/v1/token/ -H "Content-Type: application/json" -d \'{{"email":"{email}", "password":"{password}"}}\''))
        self.stdout.write(self.style.SUCCESS('\nOr using the frontend with:'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
