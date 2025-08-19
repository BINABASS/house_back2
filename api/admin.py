from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Category, Tag, Design, DesignImage, Booking, 
    Review, Favorite, Message, Notification
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'profile_picture', 'bio')}),
        (_('Designer info'), {'fields': ('company_name', 'experience')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type'),
        }),
    )


class DesignImageInline(admin.TabularInline):
    model = DesignImage
    extra = 1
    fields = ('image', 'is_primary', 'caption', 'order')
    ordering = ('order',)


@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'category', 'status', 'is_premium', 'created_at')
    list_filter = ('status', 'is_premium', 'category', 'tags')
    search_fields = ('title', 'description', 'designer__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DesignImageInline]
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'


@admin.register(DesignImage)
class DesignImageAdmin(admin.ModelAdmin):
    list_display = ('design', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('design__title', 'caption')
    date_hierarchy = 'created_at'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'designer', 'design', 'status', 'payment_status', 'start_date', 'amount')
    list_filter = ('status', 'payment_status', 'start_date')
    search_fields = ('client__email', 'designer__email', 'design__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('client', 'designer', 'design', 'status', 'payment_status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financials', {
            'fields': ('amount', 'deposit')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'designer', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('title', 'comment', 'client__email', 'designer__email')
    date_hierarchy = 'created_at'
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} reviews were approved.")
    approve_reviews.short_description = "Approve selected reviews"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'design', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'design__title')
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('subject', 'body', 'sender__email', 'recipient__email')
    date_hierarchy = 'created_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'message')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
