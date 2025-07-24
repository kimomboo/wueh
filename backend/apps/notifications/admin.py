"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Notification, EmailTemplate, EmailLog, 
    SystemAnnouncement, NotificationPreference
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""
    
    list_display = [
        'title', 'user', 'notification_type', 'is_read', 
        'is_sent', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'is_sent', 'created_at'
    ]
    search_fields = ['title', 'message', 'user__email', 'user__full_name']
    raw_id_fields = ['user', 'listing', 'payment']
    readonly_fields = ['id', 'created_at', 'read_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('listing', 'payment')
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_sent']
    
    def mark_as_read(self, request, queryset):
        """Mark notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = 'Mark as Read'
    
    def mark_as_sent(self, request, queryset):
        """Mark notifications as sent."""
        updated = queryset.update(is_sent=True)
        self.message_user(request, f'{updated} notifications marked as sent.')
    mark_as_sent.short_description = 'Mark as Sent'


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Email Template admin."""
    
    list_display = ['name', 'subject', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject']
    
    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'subject', 'is_active')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Variables', {
            'fields': ('variables',),
            'description': 'Available template variables (JSON format)'
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Email Log admin."""
    
    list_display = [
        'to_email', 'subject', 'status', 'template_name', 
        'created_at', 'sent_at'
    ]
    list_filter = ['status', 'template_name', 'created_at']
    search_fields = ['to_email', 'subject', 'user__email']
    raw_id_fields = ['user', 'notification']
    readonly_fields = ['created_at', 'sent_at']
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'notification')


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    """System Announcement admin."""
    
    list_display = [
        'title', 'announcement_type', 'is_active', 
        'start_date', 'end_date', 'created_by'
    ]
    list_filter = [
        'announcement_type', 'is_active', 'target_all_users',
        'target_premium_users', 'created_at'
    ]
    search_fields = ['title', 'message']
    raw_id_fields = ['created_by']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'message', 'announcement_type', 'is_active')
        }),
        ('Targeting', {
            'fields': (
                'target_all_users', 'target_premium_users', 'target_locations'
            )
        }),
        ('Scheduling', {
            'fields': ('start_date', 'end_date')
        }),
        ('Display Options', {
            'fields': ('show_popup', 'show_banner', 'send_notification')
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Notification Preference admin."""
    
    list_display = [
        'user', 'email_listing_expiry', 'email_payment_updates',
        'email_listing_contact', 'sms_payment_updates'
    ]
    list_filter = [
        'email_listing_expiry', 'email_payment_updates',
        'email_listing_contact', 'email_system_announcements',
        'sms_payment_updates'
    ]
    search_fields = ['user__email', 'user__full_name']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_listing_expiry', 'email_payment_updates',
                'email_listing_contact', 'email_system_announcements',
                'email_marketing'
            )
        }),
        ('Push Notifications', {
            'fields': (
                'push_listing_expiry', 'push_payment_updates',
                'push_listing_contact', 'push_system_announcements'
            )
        }),
        ('SMS Notifications', {
            'fields': ('sms_payment_updates', 'sms_security_alerts')
        }),
    )