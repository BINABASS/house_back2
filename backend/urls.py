"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Asia Design Platform API",
        default_version='v1',
        description="API documentation for Asia Design Platform",
        terms_of_service="https://www.asiadesign.com/terms/",
        contact=openapi.Contact(email="contact@asiadesign.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API URL patterns
api_patterns = [
    # API endpoints
    path('', include('api.urls')),
    
    # Authentication endpoints
    path('auth/', include('authentication.urls')),
]

urlpatterns = [
    # Root URL - render Django template
    path('', views.home, name='home'),
    
    # Admin site
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include((api_patterns, 'api'), namespace='api-v1')),
    
    # API Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Serve Swagger/ReDoc static files
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
