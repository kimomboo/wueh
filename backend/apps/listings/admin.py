"""
Admin configuration for listings app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Listing, ListingImage, ListingView, ListingContact, ListingReport


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin."""
    
    list_display = ['name', 'parent', 'listing_count_display', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    def listing_count_display(self, obj):
        """Display listing count."""
        count = obj.listings.filter(status='active').count()
        return format_html('<strong>{}</strong>', count)
    listing_count_display.short_description = 'Active Listings'


class ListingImageInline(admin.TabularInline):
    """Inline for listing images."""
    model = ListingImage
    extra = 1
    fields = ['image', 'alt_text', 'sort_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Show image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Listing admin."""
    
    list_display = [
        'title', 'seller', 'category', 'price', 'location',
        'status', 'is_premium', 'is_featured', 'views', 'created_at'
    ]
    list_filter = [
        'status', 'is_premium', 'is_featured', 'is_hot_deal',
        'category', 'location', 'condition', 'created_at'
    ]
    search_fields = ['title', 'description', 'seller__email', 'seller__full_name']
    raw_id_fields = ['seller', 'category']
    readonly_fields = [
        'id', 'views', 'unique_views', 'contact_count', 'favorites_count',
        'created_at', 'updated_at', 'published_at', 'slug'
    ]
    inlines = [ListingImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'price', 'currency', 'seller')
        }),
        ('Categorization', {
            'fields': ('category', 'condition', 'location', 'delivery_options')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_premium', 'is_featured', 'is_hot_deal')
        }),
        ('Hot Deal Settings', {
            'fields': ('original_price', 'discount_percentage'),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('views', 'unique_views', 'contact_count', 'favorites_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('slug', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_premium', 'make_featured', 'make_hot_deal', 'expire_listings']
    
    def make_premium(self, request, queryset):
        """Make selected listings premium."""
        updated = queryset.update(is_premium=True)
        self.message_user(request, f'{updated} listings marked as premium.')
    make_premium.short_description = 'Mark as Premium'
    
    def make_featured(self, request, queryset):
        """Make selected listings featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} listings marked as featured.')
    make_featured.short_description = 'Mark as Featured'
    
    def make_hot_deal(self, request, queryset):
        """Make selected listings hot deals."""
        updated = queryset.update(is_hot_deal=True)
        self.message_user(request, f'{updated} listings marked as hot deals.')
    make_hot_deal.short_description = 'Mark as Hot Deal'
    
    def expire_listings(self, request, queryset):
        """Expire selected listings."""
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} listings expired.')
    expire_listings.short_description = 'Expire Listings'
    
    def favorites_count(self, obj):
        """Get favorites count."""
        return obj.favorited_by.count()
    favorites_count.short_description = 'Favorites'


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    """Listing Image admin."""
    
    list_display = ['listing', 'image_preview', 'sort_order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'alt_text']
    raw_id_fields = ['listing']
    
    def image_preview(self, obj):
        """Show image preview."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    """Listing View admin."""
    
    list_display = ['listing', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'user__email', 'ip_address']
    raw_id_fields = ['listing', 'user']
    readonly_fields = ['created_at']


@admin.register(ListingContact)
class ListingContactAdmin(admin.ModelAdmin):
    """Listing Contact admin."""
    
    list_display = ['listing', 'user', 'contact_type', 'created_at']
    list_filter = ['contact_type', 'created_at']
    search_fields = ['listing__title', 'user__email']
    raw_id_fields = ['listing', 'user']
    readonly_fields = ['created_at']


@admin.register(ListingReport)
class ListingReportAdmin(admin.ModelAdmin):
    """Listing Report admin."""
    
    list_display = ['listing', 'reporter', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['listing__title', 'reporter__email', 'description']
    raw_id_fields = ['listing', 'reporter', 'resolved_by']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Report Details', {
            'fields': ('listing', 'reporter', 'reason', 'description')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'admin_notes', 'resolved_by', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        """Mark reports as resolved."""
        from django.utils import timezone
        updated = queryset.update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} reports marked as resolved.')
    mark_resolved.short_description = 'Mark as Resolved'