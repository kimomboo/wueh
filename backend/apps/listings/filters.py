"""
Filters for the listings app.
"""
import django_filters
from django.db.models import Q
from .models import Listing, Category


class ListingFilter(django_filters.FilterSet):
    """Filter for listings."""
    
    # Price range
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category filter
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        field_name='category'
    )
    category_slug = django_filters.CharFilter(field_name='category__slug')
    
    # Location filter
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    
    # Condition filter
    condition = django_filters.ChoiceFilter(choices=Listing.CONDITION_CHOICES)
    
    # Premium filter
    is_premium = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    is_hot_deal = django_filters.BooleanFilter()
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Seller filter
    seller = django_filters.CharFilter(field_name='seller__username')
    verified_seller = django_filters.BooleanFilter(field_name='seller__is_verified')
    
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Listing
        fields = [
            'status', 'is_premium', 'is_featured', 'is_hot_deal',
            'condition', 'location', 'category', 'seller'
        ]
    
    def filter_search(self, queryset, name, value):
        """Search across title, description, and category."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(category__name__icontains=value)
        )