"""
URL configuration for notifications app.
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:notification_id>/read/', views.mark_notification_read, name='mark-read'),
    path('<uuid:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    path('clear-all/', views.clear_all_notifications, name='clear-all'),
    path('stats/', views.notification_stats, name='notification-stats'),
    path('unread-count/', views.unread_count, name='unread-count'),
    
    # System announcements
    path('announcements/', views.SystemAnnouncementListView.as_view(), name='announcements'),
    
    # Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
]