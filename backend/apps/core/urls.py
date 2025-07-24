"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Health and config
    path('health/', views.health_check, name='health-check'),
    path('config/', views.site_config, name='site-config'),
    path('constants/', views.app_constants, name='app-constants'),
    
    # Utilities
    path('search/suggestions/', views.search_suggestions, name='search-suggestions'),
    path('contact/', views.contact_us, name='contact-us'),
]