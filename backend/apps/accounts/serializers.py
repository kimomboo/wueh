"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, UserProfile, UserActivity, UserFavorite


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    phone_number = PhoneNumberField(region='KE')
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'full_name', 'phone_number', 
            'location', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate registration data."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Validate phone number format for Kenya
        phone = attrs.get('phone_number')
        if phone:
            phone_str = str(phone)
            if not (phone_str.startswith('+2547') or phone_str.startswith('+2541')):
                raise serializers.ValidationError(
                    "Phone number must be a valid Kenyan mobile number (07xx or 01xx)."
                )
        
        return attrs
    
    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials."""
        email_or_phone = attrs.get('email_or_phone')
        password = attrs.get('password')
        
        if email_or_phone and password:
            # Try to find user by email or phone
            user = None
            if '@' in email_or_phone:
                try:
                    user = User.objects.get(email=email_or_phone)
                except User.DoesNotExist:
                    pass
            else:
                # Assume it's a phone number
                try:
                    user = User.objects.get(phone_number=email_or_phone)
                except User.DoesNotExist:
                    pass
            
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include email/phone and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    
    phone_number = PhoneNumberField(region='KE', read_only=True)
    remaining_free_ads = serializers.ReadOnlyField()
    can_post_free_ad = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'location', 'profile_picture', 'bio', 'is_verified',
            'phone_verified', 'email_verified', 'free_ads_used',
            'remaining_free_ads', 'can_post_free_ad', 'is_premium',
            'premium_expires_at', 'total_listings', 'successful_transactions',
            'rating', 'rating_count', 'created_at', 'last_active'
        ]
        read_only_fields = [
            'id', 'email', 'phone_number', 'is_verified', 'phone_verified',
            'email_verified', 'free_ads_used', 'is_premium', 'premium_expires_at',
            'total_listings', 'successful_transactions', 'rating', 'rating_count',
            'created_at', 'last_active'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'username', 'full_name', 'location', 'profile_picture', 'bio',
            'email_notifications', 'sms_notifications', 'marketing_emails'
        ]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user profile with extended info."""
    
    profile = serializers.SerializerMethodField()
    phone_number = PhoneNumberField(region='KE', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'location', 'profile_picture', 'bio', 'is_verified',
            'rating', 'rating_count', 'total_listings', 'created_at',
            'profile'
        ]
    
    def get_profile(self, obj):
        """Get extended profile information."""
        try:
            profile = obj.profile
            return {
                'business_name': profile.business_name,
                'business_description': profile.business_description,
                'website': profile.website,
                'whatsapp': profile.whatsapp,
                'show_phone': profile.show_phone,
                'show_email': profile.show_email,
            }
        except UserProfile.DoesNotExist:
            return {}


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity."""
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'description', 'metadata',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for user favorites."""
    
    listing = serializers.SerializerMethodField()
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_listing(self, obj):
        """Get basic listing information."""
        from apps.listings.serializers import ListingBasicSerializer
        return ListingBasicSerializer(obj.listing).data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password change data."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email exists."""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value