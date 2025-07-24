"""
User and Account models for PeerStorm Nexus Arena.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.models import CloudinaryField
from django.conf import settings


class User(AbstractUser):
    """Custom User model with additional fields for marketplace."""
    
    # Override email to be unique and required
    email = models.EmailField(unique=True, db_index=True)
    
    # Additional required fields
    full_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(
        unique=True, 
        region='KE',
        help_text="Kenyan mobile number (07xx or 01xx format)"
    )
    location = models.CharField(
        max_length=100,
        choices=[(county, county) for county in settings.KENYAN_COUNTIES],
        help_text="Select your county"
    )
    
    # Profile information
    profile_picture = CloudinaryField(
        'profile_pictures',
        null=True,
        blank=True,
        transformation={
            'width': 300,
            'height': 300,
            'crop': 'fill',
            'gravity': 'face'
        }
    )
    bio = models.TextField(max_length=500, blank=True)
    
    # Account status and verification
    is_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Free ads tracking
    free_ads_used = models.PositiveIntegerField(default=0)
    
    # Premium subscription
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account metrics
    total_listings = models.PositiveIntegerField(default=0)
    successful_transactions = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Account settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'phone_number', 'location']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['location']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    @property
    def can_post_free_ad(self):
        """Check if user can post a free ad."""
        return self.free_ads_used < settings.FREE_ADS_LIMIT
    
    @property
    def remaining_free_ads(self):
        """Get remaining free ads count."""
        return max(0, settings.FREE_ADS_LIMIT - self.free_ads_used)
    
    def increment_free_ads_used(self):
        """Increment free ads used counter."""
        if self.free_ads_used < settings.FREE_ADS_LIMIT:
            self.free_ads_used += 1
            self.save(update_fields=['free_ads_used'])
    
    def update_rating(self, new_rating):
        """Update user rating with new rating."""
        total_rating = (self.rating * self.rating_count) + new_rating
        self.rating_count += 1
        self.rating = total_rating / self.rating_count
        self.save(update_fields=['rating', 'rating_count'])


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Business information (optional)
    business_name = models.CharField(max_length=255, blank=True)
    business_description = models.TextField(blank=True)
    business_category = models.CharField(max_length=100, blank=True)
    
    # Social media links
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    
    # Preferences
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('sw', 'Swahili')],
        default='en'
    )
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Privacy settings
    show_phone = models.BooleanField(default=True)
    show_email = models.BooleanField(default=False)
    show_location = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"


class UserActivity(models.Model):
    """Track user activity for analytics."""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('listing_created', 'Listing Created'),
        ('listing_viewed', 'Listing Viewed'),
        ('listing_favorited', 'Listing Favorited'),
        ('message_sent', 'Message Sent'),
        ('payment_made', 'Payment Made'),
        ('profile_updated', 'Profile Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.created_at}"


class UserFavorite(models.Model):
    """User's favorite listings."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_favorites'
        verbose_name = 'User Favorite'
        verbose_name_plural = 'User Favorites'
        unique_together = ['user', 'listing']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} favorited {self.listing.title}"