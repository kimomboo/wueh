"""
Admin configuration for core app.
"""
from django.contrib import admin
from .models import SiteConfiguration, ContactMessage


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """Site Configuration admin."""
    
    list_display = ['key', 'value_preview', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['key', 'description']
    
    def value_preview(self, obj):
        """Show preview of value."""
        return obj.value[:100] + '...' if len(obj.value) > 100 else obj.value
    value_preview.short_description = 'Value'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Contact Message admin."""
    
    list_display = ['name', 'email', 'subject', 'is_read', 'is_replied', 'created_at']
    list_filter = ['is_read', 'is_replied', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_replied']
    
    def mark_as_read(self, request, queryset):
        """Mark messages as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark as Read'
    
    def mark_as_replied(self, request, queryset):
        """Mark messages as replied."""
        updated = queryset.update(is_replied=True)
        self.message_user(request, f'{updated} messages marked as replied.')
    mark_as_replied.short_description = 'Mark as Replied'