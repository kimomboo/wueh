"""
Celery tasks for the listings app.
"""
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Listing


@shared_task
def expire_free_ads():
    """Expire free ads that have reached their 4-day limit."""
    expiry_time = timezone.now()
    
    # Find free ads that should be expired
    expired_listings = Listing.objects.filter(
        status='active',
        is_premium=False,
        expires_at__lte=expiry_time
    )
    
    count = expired_listings.count()
    
    # Mark as expired
    expired_listings.update(status='expired')
    
    return f"Expired {count} free ads"


@shared_task
def cleanup_expired_listings():
    """Clean up old expired listings (older than 30 days)."""
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Delete very old expired listings
    old_expired = Listing.objects.filter(
        status='expired',
        updated_at__lt=cutoff_date
    )
    
    count = old_expired.count()
    old_expired.delete()
    
    return f"Cleaned up {count} old expired listings"


@shared_task
def update_listing_analytics():
    """Update listing analytics and rankings."""
    from django.db.models import Count, Avg
    
    # Update category listing counts
    from .models import Category
    categories = Category.objects.all()
    
    for category in categories:
        active_count = category.listings.filter(status='active').count()
        # You could store this in a separate analytics table
    
    return "Updated listing analytics"


@shared_task
def generate_hot_deals():
    """Automatically generate hot deals based on criteria."""
    from django.db.models import F
    
    # Find listings with significant price drops or high engagement
    potential_hot_deals = Listing.objects.filter(
        status='active',
        is_premium=True,
        is_hot_deal=False,
        original_price__isnull=False
    ).annotate(
        discount=F('original_price') - F('price')
    ).filter(
        discount__gt=0
    ).order_by('-discount')[:5]
    
    # Mark top deals as hot deals
    for listing in potential_hot_deals:
        if listing.original_price and listing.price:
            discount_percentage = int(((listing.original_price - listing.price) / listing.original_price) * 100)
            if discount_percentage >= 15:  # At least 15% discount
                listing.is_hot_deal = True
                listing.discount_percentage = discount_percentage
                listing.save(update_fields=['is_hot_deal', 'discount_percentage'])
    
    return f"Generated {len(potential_hot_deals)} hot deals"


@shared_task
def send_expiry_reminders():
    """Send reminders to users about expiring ads."""
    from apps.notifications.tasks import send_expiry_notification
    
    # Find ads expiring in 24 hours
    tomorrow = timezone.now() + timedelta(hours=24)
    expiring_soon = Listing.objects.filter(
        status='active',
        is_premium=False,
        expires_at__lte=tomorrow,
        expires_at__gt=timezone.now()
    ).select_related('seller')
    
    count = 0
    for listing in expiring_soon:
        send_expiry_notification.delay(listing.id)
        count += 1
    
    return f"Sent {count} expiry reminders"