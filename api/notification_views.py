from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to manage their notifications.
    
    list:
    Return a paginated list of the current user's notifications.
    
    retrieve:
    Return the details of a specific notification.
    
    mark_read:
    Mark a specific notification as read.
    
    mark_all_read:
    Mark all unread notifications as read.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['message', 'notification_type']
    filterset_fields = ['is_read', 'notification_type']
    ordering_fields = ['created_at', 'is_read']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="List all notifications for the current user.",
        responses={
            200: NotificationSerializer(many=True),
            401: 'Authentication credentials were not provided.'
        },
        tags=['Notifications']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific notification by ID.",
        responses={
            200: NotificationSerializer(),
            403: 'You do not have permission to view this notification.',
            404: 'Notification not found.'
        },
        tags=['Notifications']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        """Users can only see their own notifications."""
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Mark a specific notification as read.",
        responses={
            200: openapi.Response(
                description='Notification marked as read',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Status message'
                        )
                    }
                )
            ),
            403: 'You can only mark your own notifications as read',
            404: 'Notification not found'
        },
        tags=['Notifications']
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read.
        
        This endpoint allows users to mark a specific notification as read.
        Only the owner of the notification can mark it as read.
        """
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {'error': 'You can only mark your own notifications as read.'},
                status=status.HTTP_403_FORBIDDEN
            )
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @swagger_auto_schema(
        operation_description="Mark all unread notifications as read.",
        responses={
            200: openapi.Response(
                description='Notifications marked as read',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Status message with count of marked notifications'
                        )
                    }
                )
            ),
            400: 'No unread notifications found',
            401: 'Authentication credentials were not provided.'
        },
        tags=['Notifications']
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all unread notifications as read.
        
        This endpoint allows users to mark all their unread notifications as read
        in a single operation.
        """
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        if updated == 0:
            return Response(
                {'status': 'no unread notifications found'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response({
            'status': f'marked {updated} notification(s) as read'
        })
