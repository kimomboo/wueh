"""
Listing models for PeerStorm Nexus Arena.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from datetime import timedelta
import uuid


class Category(models.Model):
    """Listing categories."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def listing_count(self):
        """Get count of active listings in this category."""
        return self.listings.filter(status='active').count()


class Listing(models.Model):
    """Main listing model."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('sold', 'Sold'),
        ('suspended', 'Suspended'),
    ]
    
    CONDITION_CHOICES = [
        ('brand_new', 'Brand New'),
        ('like_new', 'Like New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    DELIVERY_CHOICES = [
        ('pickup_only', 'Pickup Only'),
        ('delivery_available', 'Delivery Available'),
        ('both', 'Both Pickup & Delivery'),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='KES')
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='listings')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    
    # Location and delivery
    location = models.CharField(
        max_length=100,
        choices=[(county, county) for county in settings.KENYAN_COUNTIES]
    )
    delivery_options = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    
    # Seller information
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_premium = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)  # Admin can feature listings
    is_hot_deal = models.BooleanField(default=False)  # Admin can mark as hot deal
    
    # Pricing for hot deals
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    contact_count = models.PositiveIntegerField(default=0)
    
    # SEO and search
    slug = models.SlugField(max_length=250, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    class Meta:
        db_table = 'listings'
        verbose_name = 'Listing'
        verbose_name_plural = 'Listings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_premium']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_hot_deal']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to handle business logic."""
        # Set published_at when status changes to active
        if self.status == 'active' and not self.published_at:
            self.published_at = timezone.now()
            
            # Set expiry for free ads
            if not self.is_premium:
                self.expires_at = timezone.now() + timedelta(days=settings.FREE_AD_EXPIRY_DAYS)
        
        # Generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Listing.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if listing is expired."""
        if self.is_premium:
            return False
        return self.expires_at and timezone.now() > self.expires_at
    
    @property
    def days_until_expiry(self):
        """Get days until expiry."""
        if self.is_premium or not self.expires_at:
            return None
        
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    @property
    def hours_until_expiry(self):
        """Get hours until expiry."""
        if self.is_premium or not self.expires_at:
            return None
        
        delta = self.expires_at - timezone.now()
        return max(0, delta.total_seconds() / 3600)
    
    @property
    def favorites_count(self):
        """Get favorites count."""
        return self.favorited_by.count()
    
    @property
    def main_image(self):
        """Get main listing image."""
        first_image = self.images.first()
        return first_image.image if first_image else None
    
    def increment_views(self, unique=False):
        """Increment view count."""
        self.views += 1
        if unique:
            self.unique_views += 1
        self.save(update_fields=['views', 'unique_views'])
    
    def increment_contact_count(self):
        """Increment contact count."""
        self.contact_count += 1
        self.save(update_fields=['contact_count'])
    
    def make_premium(self, days):
        """Convert listing to premium."""
        self.is_premium = True
        self.expires_at = timezone.now() + timedelta(days=days)
        self.save(update_fields=['is_premium', 'expires_at'])
    
    def expire_listing(self):
        """Mark listing as expired."""
        self.status = 'expired'
        self.save(update_fields=['status'])


class ListingImage(models.Model):
    """Listing images."""
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField(
        'listing_images',
        transformation={
            'width': 800,
            'height': 600,
            'crop': 'fill',
            'quality': 'auto:good'
        }
    )
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_images'
        verbose_name = 'Listing Image'
        verbose_name_plural = 'Listing Images'
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['listing', 'sort_order']),
        ]
    
    def __str__(self):
        return f"Image for {self.listing.title}"


class ListingView(models.Model):
    """Track listing views for analytics."""
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='view_records')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='listing_views'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_views'
        verbose_name = 'Listing View'
        verbose_name_plural = 'Listing Views'
        indexes = [
            models.Index(fields=['listing', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
        unique_together = ['listing', 'user', 'ip_address']  # Prevent duplicate views
    
    def __str__(self):
        return f"View of {self.listing.title}"


class ListingContact(models.Model):
    """Track when users contact sellers."""
    
    CONTACT_TYPES = [
        ('phone', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('message', 'Direct Message'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='contacts')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='listing_contacts'
    )
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPES)
    message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_contacts'
        verbose_name = 'Listing Contact'
        verbose_name_plural = 'Listing Contacts'
        indexes = [
            models.Index(fields=['listing', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Contact for {self.listing.title}"


class ListingReport(models.Model):
    """User reports for inappropriate listings."""
    
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake/Misleading'),
        ('duplicate', 'Duplicate Listing'),
        ('wrong_category', 'Wrong Category'),
        ('overpriced', 'Overpriced'),
        ('other', 'Other'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listing_reports'
    )
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    
    # Admin response
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'listing_reports'
        verbose_name = 'Listing Report'
        verbose_name_plural = 'Listing Reports'
        unique_together = ['listing', 'reporter']  # One report per user per listing
        indexes = [
            models.Index(fields=['listing', 'is_resolved']),
            models.Index(fields=['reporter', 'created_at']),
        ]
    
    def __str__(self):
        return f"Report for {self.listing.title} by {self.reporter.username}"