"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserActivity, UserFavorite


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""
    
    list_display = [
        'email', 'full_name', 'username', 'phone_number', 'location',
        'is_verified', 'free_ads_used', 'is_premium', 'created_at'
    ]
    list_filter = [
        'is_verified', 'is_premium', 'location', 'created_at',
        'is_active', 'is_staff'
    ]
    search_fields = ['email', 'username', 'full_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('full_name', 'email', 'phone_number', 'location', 'bio', 'profile_picture')
        }),
        ('Verification', {
            'fields': ('is_verified', 'phone_verified', 'email_verified')
        }),
        ('Marketplace', {
            'fields': ('free_ads_used', 'is_premium', 'premium_expires_at', 'rating', 'rating_count')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_active')}),
        ('Notifications', {
            'fields': ('email_notifications', 'sms_notifications', 'marketing_emails')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'phone_number', 'location', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_active', 'rating', 'rating_count']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile admin."""
    
    list_display = ['user', 'business_name', 'preferred_language', 'show_phone', 'created_at']
    list_filter = ['preferred_language', 'show_phone', 'show_email', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'business_name']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Business Info', {
            'fields': ('business_name', 'business_description', 'business_category')
        }),
        ('Social Media', {
            'fields': ('website', 'facebook', 'twitter', 'instagram', 'whatsapp')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'timezone')
        }),
        ('Privacy', {
            'fields': ('show_phone', 'show_email', 'show_location')
        }),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """User Activity admin."""
    
    list_display = ['user', 'activity_type', 'description', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__email', 'user__full_name', 'description']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """User Favorite admin."""
    
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'listing__title']
    raw_id_fields = ['user', 'listing']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'listing')