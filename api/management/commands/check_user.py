from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Check if a user exists and can authenticate'

    def handle(self, *args, **options):
        email = 'test@example.com'
        password = 'testpass123'
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f'User found: {user.email}'))
            self.stdout.write(self.style.SUCCESS(f'User is active: {user.is_active}'))
            self.stdout.write(self.style.SUCCESS(f'User is staff: {user.is_staff}'))
            self.stdout.write(self.style.SUCCESS(f'User is superuser: {user.is_superuser}'))
            
            # Try to authenticate
            if user.check_password(password):
                self.stdout.write(self.style.SUCCESS('Password is correct'))
            else:
                self.stdout.write(self.style.ERROR('Password is incorrect'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} does not exist'))
