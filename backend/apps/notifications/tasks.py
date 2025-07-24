"""
Celery tasks for the notifications app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notification, EmailLog, EmailTemplate
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_email(notification_id):
    """Send notification email."""
    try:
        notification = Notification.objects.get(id=notification_id)
        user = notification.user
        
        # Check if user wants email notifications
        if not user.email_notifications:
            return "User has disabled email notifications"
        
        # Check notification preferences
        preferences = getattr(user, 'notification_preferences', None)
        if preferences:
            notification_type = notification.notification_type
            
            # Check specific preference
            if notification_type == 'listing_expiry' and not preferences.email_listing_expiry:
                return "User disabled listing expiry emails"
            elif notification_type in ['payment_success', 'payment_failed'] and not preferences.email_payment_updates:
                return "User disabled payment update emails"
            elif notification_type == 'listing_contact' and not preferences.email_listing_contact:
                return "User disabled listing contact emails"
            elif notification_type == 'system_announcement' and not preferences.email_system_announcements:
                return "User disabled system announcement emails"
        
        # Create email log
        email_log = EmailLog.objects.create(
            user=user,
            notification=notification,
            to_email=user.email,
            subject=notification.title,
            template_name=f'notifications/{notification.notification_type}.html'
        )
        
        try:
            # Send email using Django's send_mail
            html_message = render_to_string(
                f'emails/{notification.notification_type}.html',
                {
                    'user': user,
                    'notification': notification,
                    'site_name': 'PeerStorm Nexus Arena',
                    'site_url': settings.FRONTEND_URL,
                }
            )
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=notification.title,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Update email log
            email_log.status = 'sent'
            email_log.save(update_fields=['status'])
            
            # Mark notification as sent
            notification.is_sent = True
            notification.save(update_fields=['is_sent'])
            
            return f"Email sent to {user.email}"
            
        except Exception as e:
            # Update email log with error
            email_log.status = 'failed'
            email_log.error_message = str(e)
            email_log.save(update_fields=['status', 'error_message'])
            
            logger.error(f"Failed to send email to {user.email}: {e}")
            raise
            
    except Notification.DoesNotExist:
        return "Notification not found"
    except Exception as e:
        logger.error(f"Error in send_notification_email: {e}")
        raise


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new user."""
    from apps.accounts.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            notification_type='account_verification',
            title='Welcome to PeerStorm Nexus Arena!',
            message=f'Hi {user.full_name}, welcome to Kenya\'s premier marketplace. Start listing your items today!'
        )
        
        # Send email
        send_notification_email.delay(notification.id)
        
        return f"Welcome email queued for {user.email}"
        
    except User.DoesNotExist:
        return "User not found"


@shared_task
def send_expiry_notification(listing_id):
    """Send listing expiry notification."""
    from apps.listings.models import Listing
    
    try:
        listing = Listing.objects.get(id=listing_id)
        user = listing.seller
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            listing=listing,
            notification_type='listing_expiry',
            title='Your listing is expiring soon!',
            message=f'Your listing "{listing.title}" will expire in 24 hours. Upgrade to Premium to keep it active.'
        )
        
        # Send email
        send_notification_email.delay(notification.id)
        
        return f"Expiry notification sent for listing {listing.id}"
        
    except Listing.DoesNotExist:
        return "Listing not found"


@shared_task
def send_payment_notification(payment_id, success=True):
    """Send payment notification."""
    from apps.payments.models import Payment
    
    try:
        payment = Payment.objects.get(id=payment_id)
        user = payment.user
        
        if success:
            title = 'Payment Successful!'
            message = f'Your payment of KES {payment.amount} for {payment.premium_days} days premium has been processed successfully.'
            notification_type = 'payment_success'
        else:
            title = 'Payment Failed'
            message = f'Your payment of KES {payment.amount} could not be processed. Please try again.'
            notification_type = 'payment_failed'
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            payment=payment,
            notification_type=notification_type,
            title=title,
            message=message
        )
        
        # Send email
        send_notification_email.delay(notification.id)
        
        return f"Payment notification sent for payment {payment.id}"
        
    except Payment.DoesNotExist:
        return "Payment not found"


@shared_task
def send_contact_notification(listing_id, contact_type):
    """Send notification when someone contacts seller."""
    from apps.listings.models import Listing
    
    try:
        listing = Listing.objects.get(id=listing_id)
        seller = listing.seller
        
        # Create notification
        notification = Notification.objects.create(
            user=seller,
            listing=listing,
            notification_type='listing_contact',
            title='Someone is interested in your listing!',
            message=f'A buyer contacted you about "{listing.title}" via {contact_type}.'
        )
        
        # Send email
        send_notification_email.delay(notification.id)
        
        return f"Contact notification sent for listing {listing.id}"
        
    except Listing.DoesNotExist:
        return "Listing not found"


@shared_task
def send_system_announcement(announcement_id):
    """Send system announcement to targeted users."""
    from apps.notifications.models import SystemAnnouncement
    from apps.accounts.models import User
    
    try:
        announcement = SystemAnnouncement.objects.get(id=announcement_id)
        
        # Get target users
        users = User.objects.filter(is_active=True)
        
        if not announcement.target_all_users:
            if announcement.target_premium_users:
                users = users.filter(is_premium=True)
            
            if announcement.target_locations:
                users = users.filter(location__in=announcement.target_locations)
        
        # Create notifications for all target users
        notifications = []
        for user in users:
            notification = Notification(
                user=user,
                notification_type='system_announcement',
                title=announcement.title,
                message=announcement.message
            )
            notifications.append(notification)
        
        # Bulk create notifications
        created_notifications = Notification.objects.bulk_create(notifications)
        
        # Send emails if enabled
        if announcement.send_notification:
            for notification in created_notifications:
                send_notification_email.delay(notification.id)
        
        return f"System announcement sent to {len(created_notifications)} users"
        
    except SystemAnnouncement.DoesNotExist:
        return "Announcement not found"


@shared_task
def cleanup_old_notifications():
    """Clean up old notifications (older than 90 days)."""
    from datetime import timedelta
    from django.utils import timezone
    
    cutoff_date = timezone.now() - timedelta(days=90)
    
    # Delete old read notifications
    deleted_count = Notification.objects.filter(
        is_read=True,
        created_at__lt=cutoff_date
    ).delete()[0]
    
    return f"Cleaned up {deleted_count} old notifications"


@shared_task
def send_password_reset_email(user_id, token, uid):
    """Send password reset email."""
    from apps.accounts.models import User
    
    try:
        user = User.objects.get(id=user_id)
        
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?uid={uid}&token={token}"
        
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'PeerStorm Nexus Arena',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject='Reset Your Password - PeerStorm Nexus Arena',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return f"Password reset email sent to {user.email}"
        
    except User.DoesNotExist:
        return "User not found"
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise