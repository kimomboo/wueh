"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    path('stats/', views.user_stats, name='user-stats'),
    
    # Activity and favorites
    path('activity/', views.UserActivityListView.as_view(), name='activity'),
    path('favorites/', views.UserFavoritesView.as_view(), name='favorites'),
    path('favorites/toggle/<int:listing_id>/', views.toggle_favorite, name='toggle-favorite'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
]