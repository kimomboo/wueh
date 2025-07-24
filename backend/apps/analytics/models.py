"""
Analytics models for PeerStorm Nexus Arena.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class DailyStats(models.Model):
    """Daily statistics aggregation."""
    
    date = models.DateField(unique=True)
    
    # User stats
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_users = models.PositiveIntegerField(default=0)
    
    # Listing stats
    new_listings = models.PositiveIntegerField(default=0)
    active_listings = models.PositiveIntegerField(default=0)
    expired_listings = models.PositiveIntegerField(default=0)
    premium_listings = models.PositiveIntegerField(default=0)
    
    # Payment stats
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    successful_payments = models.PositiveIntegerField(default=0)
    failed_payments = models.PositiveIntegerField(default=0)
    
    # Engagement stats
    total_views = models.PositiveIntegerField(default=0)
    total_contacts = models.PositiveIntegerField(default=0)
    total_favorites = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_stats'
        verbose_name = 'Daily Stats'
        verbose_name_plural = 'Daily Stats'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Stats for {self.date}"


class SearchQuery(models.Model):
    """Track search queries for analytics."""
    
    query = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='search_queries'
    )
    results_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField()
    
    # Filters used
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query}"


class PopularSearch(models.Model):
    """Popular search terms aggregated."""
    
    query = models.CharField(max_length=200, unique=True)
    search_count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'popular_searches'
        verbose_name = 'Popular Search'
        verbose_name_plural = 'Popular Searches'
        ordering = ['-search_count']
    
    def __str__(self):
        return f"{self.query} ({self.search_count} searches)"


class CategoryAnalytics(models.Model):
    """Analytics for categories."""
    
    category = models.ForeignKey('listings.Category', on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Listing stats
    new_listings = models.PositiveIntegerField(default=0)
    total_listings = models.PositiveIntegerField(default=0)
    premium_listings = models.PositiveIntegerField(default=0)
    
    # Engagement stats
    total_views = models.PositiveIntegerField(default=0)
    total_searches = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Percentage
    
    class Meta:
        db_table = 'category_analytics'
        verbose_name = 'Category Analytics'
        verbose_name_plural = 'Category Analytics'
        unique_together = ['category', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.category.name} - {self.date}"


class UserEngagement(models.Model):
    """Track user engagement metrics."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField()
    
    # Session data
    sessions = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0)  # In seconds
    pages_viewed = models.PositiveIntegerField(default=0)
    
    # Actions
    listings_viewed = models.PositiveIntegerField(default=0)
    searches_performed = models.PositiveIntegerField(default=0)
    contacts_made = models.PositiveIntegerField(default=0)
    favorites_added = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'user_engagement'
        verbose_name = 'User Engagement'
        verbose_name_plural = 'User Engagement'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


class RevenueAnalytics(models.Model):
    """Revenue analytics and insights."""
    
    date = models.DateField()
    
    # Revenue breakdown
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_5_days = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_7_days = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_10_days = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_15_days = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    premium_30_days = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Transaction stats
    total_transactions = models.PositiveIntegerField(default=0)
    successful_transactions = models.PositiveIntegerField(default=0)
    failed_transactions = models.PositiveIntegerField(default=0)
    
    # User metrics
    paying_users = models.PositiveIntegerField(default=0)
    new_paying_users = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'revenue_analytics'
        verbose_name = 'Revenue Analytics'
        verbose_name_plural = 'Revenue Analytics'
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Revenue for {self.date}: KES {self.total_revenue}"