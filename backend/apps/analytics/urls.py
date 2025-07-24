"""
URL configuration for analytics app.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Daily stats
    path('daily-stats/', views.DailyStatsListView.as_view(), name='daily-stats'),
    
    # Search analytics
    path('popular-searches/', views.PopularSearchesView.as_view(), name='popular-searches'),
    path('track-search/', views.track_search, name='track-search'),
    
    # Dashboard
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
    path('user/', views.user_analytics, name='user-analytics'),
    path('revenue/', views.revenue_analytics, name='revenue-analytics'),
]