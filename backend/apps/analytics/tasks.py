"""
Celery tasks for analytics.
"""
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import timedelta, date
from .models import DailyStats, CategoryAnalytics, RevenueAnalytics


@shared_task
def generate_daily_stats():
    """Generate daily statistics."""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Check if stats already exist for yesterday
    if DailyStats.objects.filter(date=yesterday).exists():
        return "Daily stats already generated for yesterday"
    
    from apps.accounts.models import User
    from apps.listings.models import Listing
    from apps.payments.models import Payment
    
    # Calculate stats for yesterday
    stats = DailyStats()
    stats.date = yesterday
    
    # User stats
    stats.new_users = User.objects.filter(
        created_at__date=yesterday
    ).count()
    
    stats.active_users = User.objects.filter(
        last_active__date=yesterday
    ).count()
    
    stats.total_users = User.objects.count()
    
    # Listing stats
    stats.new_listings = Listing.objects.filter(
        created_at__date=yesterday
    ).count()
    
    stats.active_listings = Listing.objects.filter(
        status='active'
    ).count()
    
    stats.expired_listings = Listing.objects.filter(
        status='expired',
        updated_at__date=yesterday
    ).count()
    
    stats.premium_listings = Listing.objects.filter(
        status='active',
        is_premium=True
    ).count()
    
    # Payment stats
    yesterday_payments = Payment.objects.filter(
        completed_at__date=yesterday
    )
    
    stats.total_revenue = yesterday_payments.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    stats.successful_payments = yesterday_payments.filter(
        status='completed'
    ).count()
    
    stats.failed_payments = yesterday_payments.filter(
        status='failed'
    ).count()
    
    # Engagement stats (you'd need to implement view tracking)
    from apps.listings.models import ListingView, ListingContact
    from apps.accounts.models import UserFavorite
    
    stats.total_views = ListingView.objects.filter(
        created_at__date=yesterday
    ).count()
    
    stats.total_contacts = ListingContact.objects.filter(
        created_at__date=yesterday
    ).count()
    
    stats.total_favorites = UserFavorite.objects.filter(
        created_at__date=yesterday
    ).count()
    
    stats.save()
    
    return f"Generated daily stats for {yesterday}"


@shared_task
def generate_category_analytics():
    """Generate category analytics."""
    yesterday = timezone.now().date() - timedelta(days=1)
    
    from apps.listings.models import Category, Listing
    
    categories = Category.objects.filter(is_active=True)
    
    for category in categories:
        # Check if analytics already exist
        if CategoryAnalytics.objects.filter(category=category, date=yesterday).exists():
            continue
        
        # Calculate category stats
        category_listings = Listing.objects.filter(category=category)
        
        analytics = CategoryAnalytics()
        analytics.category = category
        analytics.date = yesterday
        
        analytics.new_listings = category_listings.filter(
            created_at__date=yesterday
        ).count()
        
        analytics.total_listings = category_listings.filter(
            status='active'
        ).count()
        
        analytics.premium_listings = category_listings.filter(
            status='active',
            is_premium=True
        ).count()
        
        # Calculate average price
        avg_price = category_listings.filter(
            status='active'
        ).aggregate(avg=Avg('price'))['avg']
        analytics.average_price = avg_price or 0
        
        analytics.save()
    
    return f"Generated category analytics for {yesterday}"


@shared_task
def generate_revenue_analytics():
    """Generate revenue analytics."""
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Check if analytics already exist
    if RevenueAnalytics.objects.filter(date=yesterday).exists():
        return "Revenue analytics already generated for yesterday"
    
    from apps.payments.models import Payment
    
    yesterday_payments = Payment.objects.filter(
        completed_at__date=yesterday,
        status='completed'
    )
    
    analytics = RevenueAnalytics()
    analytics.date = yesterday
    
    # Total revenue
    analytics.total_revenue = yesterday_payments.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Revenue by plan
    for days in [5, 7, 10, 15, 30]:
        plan_revenue = yesterday_payments.filter(
            premium_days=days
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        setattr(analytics, f'premium_{days}_days', plan_revenue)
    
    # Transaction stats
    analytics.total_transactions = Payment.objects.filter(
        created_at__date=yesterday
    ).count()
    
    analytics.successful_transactions = yesterday_payments.count()
    
    analytics.failed_transactions = Payment.objects.filter(
        created_at__date=yesterday,
        status='failed'
    ).count()
    
    # User metrics
    analytics.paying_users = yesterday_payments.values('user').distinct().count()
    
    # New paying users (first time buyers)
    new_paying_users = 0
    for payment in yesterday_payments:
        if not Payment.objects.filter(
            user=payment.user,
            status='completed',
            completed_at__lt=payment.completed_at
        ).exists():
            new_paying_users += 1
    
    analytics.new_paying_users = new_paying_users
    
    analytics.save()
    
    return f"Generated revenue analytics for {yesterday}"


@shared_task
def cleanup_old_analytics():
    """Clean up old analytics data."""
    # Keep analytics for 2 years
    cutoff_date = timezone.now().date() - timedelta(days=730)
    
    # Clean up old search queries (keep for 90 days)
    search_cutoff = timezone.now().date() - timedelta(days=90)
    
    from .models import SearchQuery
    deleted_searches = SearchQuery.objects.filter(
        created_at__date__lt=search_cutoff
    ).delete()[0]
    
    return f"Cleaned up {deleted_searches} old search queries"