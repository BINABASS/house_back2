from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta

# Import models
from api.models import (
    Category, Tag, Design, DesignImage, 
    Booking, Review, Favorite, Message, Notification
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        fake = Faker()
        
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        User.objects.exclude(is_superuser=True).delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Design.objects.all().delete()
        
        # Create categories
        self.stdout.write('Creating categories...')
        categories = [
            'Living Room', 'Bedroom', 'Kitchen', 'Bathroom',
            'Office', 'Dining Room', 'Outdoor', 'Commercial'
        ]
        category_objs = [Category(name=name) for name in categories]
        Category.objects.bulk_create(category_objs)
        category_objs = list(Category.objects.all())
        
        # Create tags
        self.stdout.write('Creating tags...')
        tags = [
            'modern', 'minimalist', 'luxury', 'scandinavian', 'industrial',
            'bohemian', 'rustic', 'coastal', 'mid-century', 'contemporary'
        ]
        tag_objs = [Tag(name=name) for name in tags]
        Tag.objects.bulk_create(tag_objs)
        tag_objs = list(Tag.objects.all())
        
        # Create users
        self.stdout.write('Creating users...')
        
        # Create some clients
        clients = []
        for i in range(5):
            # Generate phone number with a maximum of 20 characters
            phone = fake.phone_number()
            if len(phone) > 20:
                phone = phone[:20]
            
            user = User.objects.create_user(
                email=f'client{i+1}@example.com',
                password='password123',
                first_name=fake.first_name()[:30],  # Limit to 30 chars
                last_name=fake.last_name()[:30],    # Limit to 30 chars
                user_type='client',
                phone=phone,
                address=fake.address()[:200],       # Limit to 200 chars
                bio=fake.text()[:500],              # Limit to 500 chars
                is_verified=True
            )
            clients.append(user)
        
        # Create some designers
        designers = []
        for i in range(5):
            # Generate phone number with a maximum of 20 characters
            phone = fake.phone_number()
            if len(phone) > 20:
                phone = phone[:20]
            
            # Generate social media usernames with length limits
            instagram = f'@{fake.user_name()}'[:50]
            facebook = fake.user_name()[:50]
            twitter = f'@{fake.user_name()}'[:15]  # Twitter handles are limited to 15 chars
            
            user = User.objects.create_user(
                email=f'designer{i+1}@example.com',
                password='password123',
                first_name=fake.first_name()[:30],  # Limit to 30 chars
                last_name=fake.last_name()[:30],    # Limit to 30 chars
                user_type='designer',
                phone=phone,
                address=fake.address()[:200],       # Limit to 200 chars
                bio=fake.text()[:500],              # Limit to 500 chars
                company_name=fake.company()[:100],  # Limit to 100 chars
                experience=random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                website=fake.url()[:200],           # Limit to 200 chars
                instagram=instagram,
                facebook=facebook,
                twitter=twitter,
                is_verified=True
            )
            designers.append(user)
        
        # Create designs
        self.stdout.write('Creating designs...')
        design_styles = ['Modern', 'Classic', 'Minimalist', 'Industrial', 'Scandinavian', 'Bohemian']
        design_types = ['Apartment', 'House', 'Office', 'Restaurant', 'Retail', 'Hotel']
        
        designs = []
        for i in range(20):
            designer = random.choice(designers)
            # Generate a title that's not too long
            title = f"{random.choice(design_styles)} {random.choice(design_types)} Design {i+1}"
            if len(title) > 200:  # Limit title to 200 chars
                title = title[:200]
                
            # Generate a description that's not too long
            description = ' '.join(fake.paragraphs(nb=3, ext_word_list=None))
            if len(description) > 1000:  # Limit description to 1000 chars
                description = description[:1000]
                
            design = Design.objects.create(
                designer=designer,
                title=title,
                description=description,
                price=random.randint(500, 5000),
                category=random.choice(category_objs),
                status=random.choices(
                    ['draft', 'pending', 'approved', 'rejected'],
                    weights=[1, 1, 8, 1],
                    k=1
                )[0],
                is_premium=random.choice([True, False, False, False]),  # 25% chance of being premium
                views=random.randint(0, 1000),
                likes=random.randint(0, 500),
                width=random.uniform(2.0, 10.0),
                height=random.uniform(2.0, 10.0)
            )
            # Add some tags to the design
            design.tags.set(random.sample(tag_objs, k=random.randint(1, 4)))
            designs.append(design)
        
        # Create bookings
        self.stdout.write('Creating bookings...')
        status_choices = ['pending', 'confirmed', 'in_progress', 'completed', 'cancelled']
        payment_status_choices = ['pending', 'paid', 'partially_paid', 'failed', 'refunded']
        
        for i in range(15):
            client = random.choice(clients)
            designer = random.choice(designers)
            design = random.choice(designs)
            start_date = timezone.now() + timedelta(days=random.randint(1, 30))
            
            Booking.objects.create(
                client=client,
                designer=designer,
                design=design,
                status=random.choice(status_choices),
                payment_status=random.choice(payment_status_choices),
                amount=random.randint(1000, 10000),
                deposit=random.randint(100, 1000),
                start_date=start_date,
                end_date=start_date + timedelta(days=random.randint(1, 14)),
                address=fake.address(),
                city=fake.city(),
                state=fake.state(),
                country=fake.country(),
                postal_code=fake.postcode(),
                notes=fake.paragraph()
            )
        
        # Create reviews
        self.stdout.write('Creating reviews...')
        for i in range(20):
            client = random.choice(clients)
            designer = random.choice(designers)
            
            Review.objects.create(
                client=client,
                designer=designer,
                rating=random.randint(1, 5),
                title=fake.sentence(),
                comment=fake.paragraph(),
                is_approved=random.choice([True, True, True, False])  # 75% chance of being approved
            )
        
        # Create favorites
        self.stdout.write('Creating favorites...')
        for i in range(30):
            user = random.choice(clients + designers)
            design = random.choice(designs)
            
            # Ensure the same user doesn't favorite the same design twice
            if not Favorite.objects.filter(user=user, design=design).exists():
                Favorite.objects.create(user=user, design=design)
        
        # Create messages
        self.stdout.write('Creating messages...')
        for i in range(50):
            sender = random.choice(clients + designers)
            # Ensure recipient is not the same as sender
            recipient = random.choice([u for u in (clients + designers) if u != sender])
            
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                subject=fake.sentence(),
                body=fake.paragraph(),
                is_read=random.choice([True, False])
            )
        
        # Create notifications
        self.stdout.write('Creating notifications...')
        notification_types = ['booking_request', 'booking_confirmed', 'new_message', 'design_approved', 'new_review']
        
        for i in range(40):
            user = random.choice(clients + designers)
            
            Notification.objects.create(
                user=user,
                notification_type=random.choice(notification_types),
                message=fake.sentence(),
                is_read=random.choice([True, False]),
                related_id=random.randint(1, 100)
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
