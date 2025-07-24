"""
Notification models for PeerStorm Nexus Arena.
"""
from django.db import models
from django.conf import settings
import uuid


class Notification(models.Model):
    """User notifications."""
    
    NOTIFICATION_TYPES = [
        ('listing_expiry', 'Listing Expiry'),
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('listing_contact', 'Listing Contact'),
        ('listing_favorite', 'Listing Favorited'),
        ('account_verification', 'Account Verification'),
        ('system_announcement', 'System Announcement'),
        ('premium_upgrade', 'Premium Upgrade'),
        ('listing_approved', 'Listing Approved'),
        ('listing_rejected', 'Listing Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional related objects
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, null=True, blank=True)
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)  # For email/SMS notifications
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class EmailTemplate(models.Model):
    """Email templates for different notification types."""
    
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    # Template variables documentation
    variables = models.JSONField(
        default=list,
        help_text="List of available template variables"
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_templates'
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    def __str__(self):
        return self.name


class EmailLog(models.Model):
    """Log of sent emails."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('delivered', 'Delivered'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_logs')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True)
    
    to_email = models.EmailField()
    subject = models.CharField(max_length=200)
    template_name = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # External service data
    external_id = models.CharField(max_length=100, blank=True)  # Resend message ID
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Email to {self.to_email} - {self.status}"


class SystemAnnouncement(models.Model):
    """System-wide announcements."""
    
    ANNOUNCEMENT_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('maintenance', 'Maintenance'),
        ('feature', 'New Feature'),
        ('promotion', 'Promotion'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='info')
    
    # Targeting
    target_all_users = models.BooleanField(default=True)
    target_premium_users = models.BooleanField(default=False)
    target_locations = models.JSONField(default=list, blank=True)  # List of counties
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Display options
    show_popup = models.BooleanField(default=False)
    show_banner = models.BooleanField(default=True)
    send_notification = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_announcements'
        verbose_name = 'System Announcement'
        verbose_name_plural = 'System Announcements'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NotificationPreference(models.Model):
    """User notification preferences."""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notification_preferences'
    )
    
    # Email notifications
    email_listing_expiry = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_listing_contact = models.BooleanField(default=True)
    email_system_announcements = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    
    # Push notifications (for future mobile app)
    push_listing_expiry = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)
    push_listing_contact = models.BooleanField(default=True)
    push_system_announcements = models.BooleanField(default=False)
    
    # SMS notifications (for critical updates)
    sms_payment_updates = models.BooleanField(default=True)
    sms_security_alerts = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"