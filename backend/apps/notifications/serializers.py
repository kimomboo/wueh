"""
Serializers for the notifications app.
"""
from rest_framework import serializers
from .models import Notification, SystemAnnouncement, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'listing_title', 'is_read', 'created_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_time_ago(self, obj):
        """Get human-readable time ago."""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return obj.created_at.strftime('%b %d, %Y')


class SystemAnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for system announcements."""
    
    class Meta:
        model = SystemAnnouncement
        fields = [
            'id', 'title', 'message', 'announcement_type',
            'show_popup', 'show_banner', 'start_date', 'end_date'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_listing_expiry', 'email_payment_updates', 'email_listing_contact',
            'email_system_announcements', 'email_marketing', 'push_listing_expiry',
            'push_payment_updates', 'push_listing_contact', 'push_system_announcements',
            'sms_payment_updates', 'sms_security_alerts'
        ]
    
    def update(self, instance, validated_data):
        """Update notification preferences."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    read_notifications = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = NotificationSerializer(many=True)