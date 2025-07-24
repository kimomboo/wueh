"""
Serializers for the listings app.
"""
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import Category, Listing, ListingImage, ListingView, ListingContact, ListingReport
from apps.accounts.serializers import UserProfileDetailSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    listing_count = serializers.ReadOnlyField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'parent',
            'listing_count', 'subcategories', 'sort_order'
        ]
    
    def get_subcategories(self, obj):
        """Get subcategories if this is a parent category."""
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []


class ListingImageSerializer(serializers.ModelSerializer):
    """Serializer for listing images."""
    
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'alt_text', 'sort_order']
        read_only_fields = ['id']


class ListingBasicSerializer(serializers.ModelSerializer):
    """Basic listing serializer for lists and references."""
    
    main_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)
    seller_verified = serializers.BooleanField(source='seller.is_verified', read_only=True)
    seller_rating = serializers.DecimalField(source='seller.rating', max_digits=3, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    favorites_count = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    hours_until_expiry = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price', 'currency', 'location', 'condition',
            'status', 'is_premium', 'is_featured', 'is_hot_deal',
            'original_price', 'discount_percentage', 'main_image',
            'seller_name', 'seller_verified', 'seller_rating',
            'category_name', 'favorites_count', 'views', 'created_at',
            'days_until_expiry', 'hours_until_expiry', 'is_expired'
        ]
    
    def get_main_image(self, obj):
        """Get main listing image URL."""
        main_image = obj.main_image
        return str(main_image) if main_image else None


class ListingDetailSerializer(serializers.ModelSerializer):
    """Detailed listing serializer."""
    
    images = ListingImageSerializer(many=True, read_only=True)
    seller = UserProfileDetailSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    favorites_count = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    hours_until_expiry = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'currency',
            'category', 'condition', 'location', 'delivery_options',
            'seller', 'status', 'is_premium', 'is_featured', 'is_hot_deal',
            'original_price', 'discount_percentage', 'images',
            'favorites_count', 'views', 'unique_views', 'contact_count',
            'created_at', 'updated_at', 'published_at', 'expires_at',
            'days_until_expiry', 'hours_until_expiry', 'is_expired',
            'is_favorited', 'slug', 'meta_description'
        ]
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this listing."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating listings."""
    
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=True,
        min_length=1,
        max_length=10
    )
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'price', 'currency', 'category',
            'condition', 'location', 'delivery_options', 'images'
        ]
    
    def validate_images(self, value):
        """Validate uploaded images."""
        if len(value) < 1:
            raise serializers.ValidationError("At least one image is required.")
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed.")
        
        # Validate image size (max 5MB per image)
        for image in value:
            if image.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Each image must be less than 5MB.")
        
        return value
    
    def create(self, validated_data):
        """Create listing with images."""
        images_data = validated_data.pop('images')
        user = self.context['request'].user
        
        # Check if user can post free ad
        if not user.can_post_free_ad:
            raise serializers.ValidationError(
                "You have used all 3 free ads. Future listings must be Premium."
            )
        
        with transaction.atomic():
            # Create listing
            listing = Listing.objects.create(
                seller=user,
                status='active',
                **validated_data
            )
            
            # Create images
            for i, image_data in enumerate(images_data):
                ListingImage.objects.create(
                    listing=listing,
                    image=image_data,
                    sort_order=i
                )
            
            # Increment user's free ads used
            user.increment_free_ads_used()
            
            # Update user's total listings count
            user.total_listings += 1
            user.save(update_fields=['total_listings'])
        
        return listing


class ListingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating listings."""
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'price', 'category',
            'condition', 'location', 'delivery_options'
        ]
    
    def validate(self, attrs):
        """Validate update data."""
        listing = self.instance
        
        # Only allow updates if listing is active or draft
        if listing.status not in ['active', 'draft']:
            raise serializers.ValidationError("Cannot update expired or sold listings.")
        
        # Only seller can update
        if listing.seller != self.context['request'].user:
            raise serializers.ValidationError("You can only update your own listings.")
        
        return attrs


class ListingContactSerializer(serializers.ModelSerializer):
    """Serializer for listing contacts."""
    
    class Meta:
        model = ListingContact
        fields = ['contact_type', 'message']
    
    def create(self, validated_data):
        """Create contact record."""
        request = self.context['request']
        listing = self.context['listing']
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        contact = ListingContact.objects.create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            **validated_data
        )
        
        # Increment listing contact count
        listing.increment_contact_count()
        
        return contact


class ListingReportSerializer(serializers.ModelSerializer):
    """Serializer for reporting listings."""
    
    class Meta:
        model = ListingReport
        fields = ['reason', 'description']
    
    def create(self, validated_data):
        """Create report."""
        request = self.context['request']
        listing = self.context['listing']
        
        # Check if user already reported this listing
        if ListingReport.objects.filter(listing=listing, reporter=request.user).exists():
            raise serializers.ValidationError("You have already reported this listing.")
        
        return ListingReport.objects.create(
            listing=listing,
            reporter=request.user,
            **validated_data
        )


class HotDealSerializer(serializers.ModelSerializer):
    """Serializer for hot deals."""
    
    main_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)
    seller_verified = serializers.BooleanField(source='seller.is_verified', read_only=True)
    seller_rating = serializers.DecimalField(source='seller.rating', max_digits=3, decimal_places=2, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    savings_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price', 'original_price', 'discount_percentage',
            'currency', 'location', 'main_image', 'seller_name',
            'seller_verified', 'seller_rating', 'category_name',
            'views', 'savings_amount', 'created_at'
        ]
    
    def get_main_image(self, obj):
        """Get main listing image URL."""
        main_image = obj.main_image
        return str(main_image) if main_image else None
    
    def get_savings_amount(self, obj):
        """Calculate savings amount."""
        if obj.original_price and obj.discount_percentage:
            return obj.original_price - obj.price
        return 0