"""
Views for the accounts app.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from .models import User, UserProfile, UserActivity, UserFavorite
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, UserProfileDetailSerializer,
    UserActivitySerializer, UserFavoriteSerializer, PasswordChangeSerializer,
    PasswordResetSerializer
)
from apps.core.utils import log_user_activity


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user account."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Log registration activity
        log_user_activity(
            user=user,
            activity_type='registration',
            description='User registered successfully',
            request=request
        )
        
        # Send welcome email (async task)
        from apps.notifications.tasks import send_welcome_email
        send_welcome_email.delay(user.id)
        
        return Response({
            'message': 'Registration successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """User login endpoint."""
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Authenticate user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last active
        user.last_active = timezone.now()
        user.save(update_fields=['last_active'])
        
        # Log login activity
        log_user_activity(
            user=user,
            activity_type='login',
            description='User logged in successfully',
            request=request
        )
        
        return Response({
            'message': 'Login successful',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get current user."""
        return self.request.user
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        response = super().update(request, *args, **kwargs)
        
        # Log profile update activity
        log_user_activity(
            user=request.user,
            activity_type='profile_updated',
            description='User updated profile',
            request=request
        )
        
        return response


class UserDetailView(generics.RetrieveAPIView):
    """Public user profile view."""
    
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'


class UserActivityListView(generics.ListAPIView):
    """User activity history."""
    
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's activities."""
        return UserActivity.objects.filter(user=self.request.user)


class UserFavoritesView(generics.ListAPIView):
    """User's favorite listings."""
    
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's favorites."""
        return UserFavorite.objects.filter(user=self.request.user).select_related('listing')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favorite(request, listing_id):
    """Toggle listing favorite status."""
    from apps.listings.models import Listing
    
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    favorite, created = UserFavorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if not created:
        favorite.delete()
        favorited = False
    else:
        favorited = True
        # Log favorite activity
        log_user_activity(
            user=request.user,
            activity_type='listing_favorited',
            description=f'User favorited listing: {listing.title}',
            metadata={'listing_id': listing.id},
            request=request
        )
    
    return Response({
        'favorited': favorited,
        'favorites_count': listing.favorited_by.count()
    })


class PasswordChangeView(generics.GenericAPIView):
    """Change user password."""
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Log password change activity
        log_user_activity(
            user=user,
            activity_type='password_changed',
            description='User changed password',
            request=request
        )
        
        return Response({'message': 'Password changed successfully'})


class PasswordResetRequestView(generics.GenericAPIView):
    """Request password reset."""
    
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Send password reset email."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send reset email (async task)
        from apps.notifications.tasks import send_password_reset_email
        send_password_reset_email.delay(user.id, token, uid)
        
        return Response({
            'message': 'Password reset email sent successfully'
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request):
    """Confirm password reset with token."""
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not all([uid, token, new_password]):
        return Response(
            {'error': 'Missing required fields'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not default_token_generator.check_token(user, token):
        return Response(
            {'error': 'Invalid or expired reset link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password
    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return Response(
            {'error': list(e.messages)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    # Log password reset activity
    log_user_activity(
        user=user,
        activity_type='password_reset',
        description='User reset password via email',
        request=request
    )
    
    return Response({'message': 'Password reset successful'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Get user statistics."""
    user = request.user
    
    # Get user's listings stats
    from apps.listings.models import Listing
    listings = Listing.objects.filter(seller=user)
    
    stats = {
        'total_listings': listings.count(),
        'active_listings': listings.filter(status='active').count(),
        'expired_listings': listings.filter(status='expired').count(),
        'premium_listings': listings.filter(is_premium=True).count(),
        'total_views': sum(listing.views for listing in listings),
        'total_favorites': UserFavorite.objects.filter(listing__seller=user).count(),
        'free_ads_used': user.free_ads_used,
        'remaining_free_ads': user.remaining_free_ads,
        'can_post_free_ad': user.can_post_free_ad,
        'rating': float(user.rating),
        'rating_count': user.rating_count,
        'member_since': user.created_at,
        'last_active': user.last_active,
    }
    
    return Response(stats)