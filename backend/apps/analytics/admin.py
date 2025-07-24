"""
Admin configuration for analytics app.
"""
from django.contrib import admin
from .models import DailyStats, SearchQuery, PopularSearch, CategoryAnalytics, RevenueAnalytics


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    """Daily Stats admin."""
    
    list_display = [
        'date', 'new_users', 'active_users', 'new_listings',
        'total_revenue', 'successful_payments'
    ]
    list_filter = ['date']
    readonly_fields = ['created_at']
    ordering = ['-date']


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """Search Query admin."""
    
    list_display = ['query', 'user', 'results_count', 'category', 'location', 'created_at']
    list_filter = ['category', 'location', 'created_at']
    search_fields = ['query', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']


@admin.register(PopularSearch)
class PopularSearchAdmin(admin.ModelAdmin):
    """Popular Search admin."""
    
    list_display = ['query', 'search_count', 'last_searched']
    ordering = ['-search_count']
    readonly_fields = ['last_searched']


@admin.register(CategoryAnalytics)
class CategoryAnalyticsAdmin(admin.ModelAdmin):
    """Category Analytics admin."""
    
    list_display = [
        'category', 'date', 'new_listings', 'total_listings',
        'total_views', 'average_price'
    ]
    list_filter = ['date', 'category']
    raw_id_fields = ['category']


@admin.register(RevenueAnalytics)
class RevenueAnalyticsAdmin(admin.ModelAdmin):
    """Revenue Analytics admin."""
    
    list_display = [
        'date', 'total_revenue', 'total_transactions',
        'successful_transactions', 'paying_users'
    ]
    list_filter = ['date']
    ordering = ['-date']