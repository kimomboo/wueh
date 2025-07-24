"""
Views for the analytics app.
"""
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import DailyStats, SearchQuery, PopularSearch, CategoryAnalytics
from .serializers import (
    DailyStatsSerializer, SearchQuerySerializer, PopularSearchSerializer,
    CategoryAnalyticsSerializer, AnalyticsDashboardSerializer
)


class DailyStatsListView(generics.ListAPIView):
    """List daily statistics."""
    
    serializer_class = DailyStatsSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get daily stats for specified period."""
        days = int(self.request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        return DailyStats.objects.filter(date__gte=start_date).order_by('-date')


class PopularSearchesView(generics.ListAPIView):
    """List popular search terms."""
    
    serializer_class = PopularSearchSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get top search terms."""
        return PopularSearch.objects.order_by('-search_count')[:20]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_search(request):
    """Track search query for analytics."""
    query = request.data.get('query', '').strip()
    if not query:
        return Response({'error': 'Query is required'}, status=400)
    
    # Get client IP
    from apps.core.utils import get_client_ip
    ip_address = get_client_ip(request)
    
    # Create search record
    search_data = {
        'query': query,
        'user': request.user if request.user.is_authenticated else None,
        'ip_address': ip_address,
        'results_count': request.data.get('results_count', 0),
        'category': request.data.get('category', ''),
        'location': request.data.get('location', ''),
        'min_price': request.data.get('min_price'),
        'max_price': request.data.get('max_price'),
    }
    
    SearchQuery.objects.create(**search_data)
    
    # Update popular searches
    popular_search, created = PopularSearch.objects.get_or_create(
        query=query,
        defaults={'search_count': 1}
    )
    
    if not created:
        popular_search.search_count += 1
        popular_search.save(update_fields=['search_count', 'last_searched'])
    
    return Response({'message': 'Search tracked successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def analytics_dashboard(request):
    """Get analytics dashboard data."""
    from apps.accounts.models import User
    from apps.listings.models import Listing
    from apps.payments.models import Payment
    
    # Calculate date ranges
    today = timezone.now().date()
    last_month = today - timedelta(days=30)
    previous_month = today - timedelta(days=60)
    
    # Current stats
    total_users = User.objects.count()
    total_listings = Listing.objects.filter(status='active').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    active_premium_listings = Listing.objects.filter(
        status='active', is_premium=True
    ).count()
    
    # Growth calculations
    last_month_users = User.objects.filter(created_at__gte=last_month).count()
    previous_month_users = User.objects.filter(
        created_at__gte=previous_month,
        created_at__lt=last_month
    ).count()
    
    user_growth = calculate_growth_percentage(last_month_users, previous_month_users)
    
    last_month_listings = Listing.objects.filter(created_at__gte=last_month).count()
    previous_month_listings = Listing.objects.filter(
        created_at__gte=previous_month,
        created_at__lt=last_month
    ).count()
    
    listing_growth = calculate_growth_percentage(last_month_listings, previous_month_listings)
    
    last_month_revenue = Payment.objects.filter(
        status='completed',
        completed_at__gte=last_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    previous_month_revenue = Payment.objects.filter(
        status='completed',
        completed_at__gte=previous_month,
        completed_at__lt=last_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_growth = calculate_growth_percentage(
        float(last_month_revenue), float(previous_month_revenue)
    )
    
    # Recent stats
    recent_stats = DailyStats.objects.filter(date__gte=last_month).order_by('-date')[:30]
    
    # Popular searches
    popular_searches = PopularSearch.objects.order_by('-search_count')[:10]
    
    # Top categories
    top_categories = CategoryAnalytics.objects.filter(
        date__gte=last_month
    ).values('category__name').annotate(
        total_listings=Sum('total_listings'),
        total_views=Sum('total_views')
    ).order_by('-total_listings')[:10]
    
    dashboard_data = {
        'total_users': total_users,
        'total_listings': total_listings,
        'total_revenue': total_revenue,
        'active_premium_listings': active_premium_listings,
        'user_growth': user_growth,
        'listing_growth': listing_growth,
        'revenue_growth': revenue_growth,
        'recent_stats': DailyStatsSerializer(recent_stats, many=True).data,
        'popular_searches': PopularSearchSerializer(popular_searches, many=True).data,
        'top_categories': list(top_categories)
    }
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_analytics(request):
    """Get analytics for current user."""
    user = request.user
    
    # User's listing stats
    from apps.listings.models import Listing
    user_listings = Listing.objects.filter(seller=user)
    
    stats = {
        'total_listings': user_listings.count(),
        'active_listings': user_listings.filter(status='active').count(),
        'expired_listings': user_listings.filter(status='expired').count(),
        'premium_listings': user_listings.filter(is_premium=True).count(),
        'total_views': sum(listing.views for listing in user_listings),
        'total_favorites': user.favorites.count(),
        'free_ads_used': user.free_ads_used,
        'remaining_free_ads': user.remaining_free_ads,
    }
    
    # Recent activity
    from apps.accounts.models import UserActivity
    recent_activity = UserActivity.objects.filter(user=user).order_by('-created_at')[:10]
    
    stats['recent_activity'] = [
        {
            'activity_type': activity.activity_type,
            'description': activity.description,
            'created_at': activity.created_at
        }
        for activity in recent_activity
    ]
    
    return Response(stats)


def calculate_growth_percentage(current, previous):
    """Calculate growth percentage."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return round(((current - previous) / previous) * 100, 2)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def revenue_analytics(request):
    """Get detailed revenue analytics."""
    from apps.payments.models import Payment
    
    # Get date range
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Revenue by plan
    revenue_by_plan = Payment.objects.filter(
        status='completed',
        completed_at__gte=start_date
    ).values('premium_days').annotate(
        total_revenue=Sum('amount'),
        transaction_count=Count('id')
    ).order_by('-total_revenue')
    
    # Daily revenue
    daily_revenue = Payment.objects.filter(
        status='completed',
        completed_at__gte=start_date
    ).extra(
        select={'day': 'date(completed_at)'}
    ).values('day').annotate(
        revenue=Sum('amount'),
        transactions=Count('id')
    ).order_by('day')
    
    # Payment method breakdown
    payment_methods = Payment.objects.filter(
        status='completed',
        completed_at__gte=start_date
    ).values('payment_method').annotate(
        total_revenue=Sum('amount'),
        transaction_count=Count('id')
    )
    
    return Response({
        'revenue_by_plan': list(revenue_by_plan),
        'daily_revenue': list(daily_revenue),
        'payment_methods': list(payment_methods),
        'date_range': {
            'start_date': start_date.date(),
            'end_date': timezone.now().date(),
            'days': days
        }
    })