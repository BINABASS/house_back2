from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model that supports using email instead of username."""
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('designer', 'Designer'),
    )
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    # Additional fields for designers
    company_name = models.CharField(max_length=100, blank=True)
    experience = models.PositiveIntegerField(default=0, help_text="Years of experience")
    
    # Social media links
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Category(models.Model):
    """Design categories like Living Room, Bedroom, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class for frontend display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags for designs to improve searchability."""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Design(models.Model):
    """Design model representing interior design projects."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    designer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='designs'
    )
    tags = models.ManyToManyField(Tag, related_name='designs', blank=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
    is_premium = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    width = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Width in meters"
    )
    height = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Height in meters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_premium']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment the view count."""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])
    



class DesignImage(models.Model):
    """Images associated with a design."""
    design = models.ForeignKey(
        Design, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='designs/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.design.title} - Image {self.id}"


class Booking(models.Model):
    """Booking model for clients to book design services."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_bookings'
    )
    designer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='designer_bookings'
    )
    design = models.ForeignKey(
        Design, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='bookings'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    payment_status = models.CharField(
        max_length=15, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    deposit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.client.email} to {self.designer.email}"
    
    @property
    def duration_days(self):
        """Calculate the duration of the booking in days."""
        if not self.end_date:
            return 1
        return (self.end_date - self.start_date).days + 1


class Review(models.Model):
    """Reviews for designers by clients."""
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_given'
    )
    designer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews_received'
    )
    booking = models.OneToOneField(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='review',
        null=True,
        blank=True
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('client', 'designer', 'booking')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rating} stars by {self.client.email}"


class Favorite(models.Model):
    """Allow users to favorite designs."""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    design = models.ForeignKey(
        Design, 
        on_delete=models.CASCADE, 
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'design')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} favorited {self.design.title}"


class Message(models.Model):
    """Messages between users."""
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='messages',
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.email} to {self.recipient.email}: {self.subject}"


class Notification(models.Model):
    """System notifications for users."""
    NOTIFICATION_TYPES = (
        ('booking_request', 'Booking Request'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('new_message', 'New Message'),
        ('new_review', 'New Review'),
        ('design_approved', 'Design Approved'),
        ('design_rejected', 'Design Rejected'),
        ('payment_received', 'Payment Received'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="ID of the related object (booking, design, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.email}"
