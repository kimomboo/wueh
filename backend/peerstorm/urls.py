"""
URL configuration for PeerStorm Nexus Arena project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# API Router
router = DefaultRouter()

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/listings/', include('apps.listings.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/core/', include('apps.core.urls')),
    
    # Health check
    path('health/', include('apps.core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "PeerStorm Nexus Arena Admin"
admin.site.site_title = "PeerStorm Admin"
admin.site.index_title = "Welcome to PeerStorm Administration"