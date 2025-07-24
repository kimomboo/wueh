"""
Serializers for the analytics app.
"""
from rest_framework import serializers
from .models import DailyStats, SearchQuery, PopularSearch, CategoryAnalytics


class DailyStatsSerializer(serializers.ModelSerializer):
    """Serializer for daily statistics."""
    
    class Meta:
        model = DailyStats
        fields = [
            'date', 'new_users', 'active_users', 'total_users',
            'new_listings', 'active_listings', 'expired_listings', 'premium_listings',
            'total_revenue', 'successful_payments', 'failed_payments',
            'total_views', 'total_contacts', 'total_favorites'
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search queries."""
    
    class Meta:
        model = SearchQuery
        fields = [
            'query', 'results_count', 'category', 'location',
            'min_price', 'max_price', 'created_at'
        ]
        read_only_fields = ['created_at']


class PopularSearchSerializer(serializers.ModelSerializer):
    """Serializer for popular searches."""
    
    class Meta:
        model = PopularSearch
        fields = ['query', 'search_count', 'last_searched']


class CategoryAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for category analytics."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CategoryAnalytics
        fields = [
            'category_name', 'date', 'new_listings', 'total_listings',
            'premium_listings', 'total_views', 'total_searches',
            'average_price', 'conversion_rate'
        ]


class AnalyticsDashboardSerializer(serializers.Serializer):
    """Serializer for analytics dashboard data."""
    
    # Overview stats
    total_users = serializers.IntegerField()
    total_listings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    active_premium_listings = serializers.IntegerField()
    
    # Growth metrics
    user_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    listing_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    revenue_growth = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Recent activity
    recent_stats = DailyStatsSerializer(many=True)
    popular_searches = PopularSearchSerializer(many=True)
    top_categories = CategoryAnalyticsSerializer(many=True)