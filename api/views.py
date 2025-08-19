from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Category, Tag, Design, DesignImage
from .serializers import (
    UserSerializer, CategorySerializer, TagSerializer,
    DesignSerializer, DesignImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DesignViewSet(viewsets.ModelViewSet):
    """
    Flow:
      1) POST /designs/ with {title, description, price, category_id, tag_ids[]} -> creates the Design (no images yet)
      2) POST /designs/{id}/upload_images/ with form-data images[] -> attaches images
    """
    queryset = Design.objects.all()
    serializer_class = DesignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_premium', 'designer']
    search_fields = ['title', 'description', 'tags__name', 'category__name']
    ordering_fields = ['created_at', 'price', 'views', 'likes']
    ordering = ['-created_at']
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('images', 'tags', 'category')
        user = self.request.user
        if not getattr(user, 'is_staff', False):
            if getattr(user, 'is_authenticated', False):
                qs = qs.filter(Q(status='approved') | Q(designer=user))
            else:
                qs = qs.filter(status='approved')
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(designer=self.request.user, status='pending')

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        """
        form-data:
          images: file (can be multiple)
          is_primary: optional (true/false) - applies to the first image only if provided
          caption: optional - applies to each image if a single one; ignores for multiple
        """
        design = self.get_object()
        if design.designer != request.user and not request.user.is_staff:
            raise PermissionDenied("Not authorized to add images to this design.")

        files = request.FILES.getlist('images')
        if not files:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        for idx, f in enumerate(files):
            created.append(
                DesignImage.objects.create(
                    design=design,
                    image=f,
                    is_primary=str(request.data.get('is_primary', '')).lower() == 'true' if idx == 0 else False,
                    caption=request.data.get('caption', '')
                )
            )
        return Response(DesignImageSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        design = self.get_object()
        design.likes = (design.likes or 0) + 1
        design.save(update_fields=['likes'])
        return Response({'status': 'design liked', 'likes': design.likes})
        

class DesignImageViewSet(viewsets.ModelViewSet):
    serializer_class = DesignImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Short-circuit during schema generation or if lookup is missing
        if getattr(self, 'swagger_fake_view', False):
            return DesignImage.objects.none()
        design_pk = self.kwargs.get('design_pk')
        if not design_pk:
            return DesignImage.objects.none()
        # for nested route /designs/{design_pk}/images/
        return DesignImage.objects.filter(design_id=design_pk).select_related('design')

    def perform_create(self, serializer):
        design = get_object_or_404(Design, pk=self.kwargs['design_pk'])
        if design.designer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You don't have permission to add images to this design.")
        serializer.save(design=design)
