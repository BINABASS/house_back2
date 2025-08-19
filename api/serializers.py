from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Design, DesignImage, Booking, Notification
from django.utils.text import slugify
from uuid import uuid4

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'user_type',
            'phone', 'address', 'bio', 'profile_picture', 'company_name',
            'experience', 'website', 'instagram', 'facebook', 'twitter',
            'date_joined', 'last_login', 'password'
        ]
        read_only_fields = ('date_joined', 'last_login')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class DesignImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignImage
        fields = ['id', 'image', 'is_primary', 'caption', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class DesignSerializer(serializers.ModelSerializer):
    # Read-only nested
    designer = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = DesignImageSerializer(many=True, read_only=True)

    # Write-only input (IDs)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        required=False,
        write_only=True
    )

    class Meta:
        model = Design
        fields = [
            'id', 'title', 'description', 'price', 'designer',
            'category', 'category_id', 'tags', 'tag_ids', 'status',
            'is_premium', 'views', 'likes', 'width', 'height', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'designer', 'views', 'likes', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        design = Design.objects.create(**validated_data)
        if tags:
            design.tags.set(tags)
        return design


class BookingSerializer(serializers.ModelSerializer):
    # Read-only nested fields
    client = UserSerializer(read_only=True)
    designer = UserSerializer(read_only=True)
    design = DesignSerializer(read_only=True)

    # Write-only input
    design_id = serializers.PrimaryKeyRelatedField(
        queryset=Design.objects.all(), source='design', write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'designer', 'design', 'design_id', 'status', 'payment_status',
            'amount', 'deposit', 'start_date', 'end_date', 'address', 'city', 'state',
            'country', 'postal_code', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'designer', 'status', 'payment_status', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        design: Design = validated_data['design']

        # Set parties
        validated_data['client'] = user
        validated_data['designer'] = design.designer

        # Default amounts if not provided
        if 'amount' not in validated_data or validated_data['amount'] in (None, ''):
            validated_data['amount'] = design.price
        if 'deposit' not in validated_data or validated_data['deposit'] in (None, ''):
            validated_data['deposit'] = 0

        # Initial statuses
        validated_data['status'] = 'pending'
        validated_data['payment_status'] = 'pending'

        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'is_read', 'related_id', 'created_at']
        read_only_fields = ['id', 'created_at']
