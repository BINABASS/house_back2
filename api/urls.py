from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CategoryViewSet, TagViewSet, DesignViewSet, DesignImageViewSet, BookingViewSet

# ==============================
# Main router
# ==============================
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'designs', DesignViewSet, basename='design')
router.register(r'bookings', BookingViewSet, basename='booking')

# ==============================
# Nested router for design images
# ==============================
design_router = routers.NestedSimpleRouter(router, r'designs', lookup='design')
design_router.register(r'images', DesignImageViewSet, basename='design-image')

# ==============================
# URL patterns
# ==============================
urlpatterns = [
    # API routes
    path('', include(router.urls)),              # /api/v1/categories/, /api/v1/tags/, /api/v1/designs/
    path('', include(design_router.urls)),       # /api/v1/designs/<design_pk>/images/

    # DRF browsable API login/logout
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),

    # JWT authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),   # /api/v1/token/
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # /api/v1/token/refresh/
]
