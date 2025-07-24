"""
Views for the listings app.
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Category, Listing, ListingImage, ListingView, ListingContact
from .serializers import (
    CategorySerializer, ListingBasicSerializer, ListingDetailSerializer,
    ListingCreateSerializer, ListingUpdateSerializer, ListingContactSerializer,
    ListingReportSerializer, HotDealSerializer
)
from .filters import ListingFilter
from apps.core.utils import get_client_ip, log_user_activity
from apps.core.pagination import StandardResultsSetPagination


class CategoryListView(generics.ListAPIView):
    """List all categories with listing counts."""
    
    queryset = Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get categories with listing counts."""
        return self.queryset.annotate(
            listing_count=Count('listings', filter=Q(listings__status='active'))
        ).order_by('sort_order', 'name')


class ListingListView(generics.ListAPIView):
    """List listings with filtering and search."""
    
    queryset = Listing.objects.filter(status='active').select_related(
        'seller', 'category'
    ).prefetch_related('images', 'favorited_by')
    serializer_class = ListingBasicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price', 'views']
    ordering = ['-is_premium', '-is_featured', '-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get filtered listings."""
        queryset = self.queryset
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(
                Q(category__slug=category) | Q(category__name__icontains=category)
            )
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Filter premium only
        premium_only = self.request.query_params.get('premium_only')
        if premium_only == 'true':
            queryset = queryset.filter(is_premium=True)
        
        return queryset


class ListingDetailView(generics.RetrieveAPIView):
    """Get listing details."""
    
    queryset = Listing.objects.select_related('seller', 'category').prefetch_related(
        'images', 'favorited_by'
    )
    serializer_class = ListingDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        """Get listing and track view."""
        listing = self.get_object()
        
        # Track view
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check if this is a unique view
        is_unique = not ListingView.objects.filter(
            listing=listing,
            ip_address=ip_address
        ).exists()
        
        # Create view record
        ListingView.objects.get_or_create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            defaults={'user_agent': user_agent}
        )
        
        # Increment view count
        listing.increment_views(unique=is_unique)
        
        # Log activity if user is authenticated
        if request.user.is_authenticated:
            log_user_activity(
                user=request.user,
                activity_type='listing_viewed',
                description=f'Viewed listing: {listing.title}',
                metadata={'listing_id': str(listing.id)},
                request=request
            )
        
        serializer = self.get_serializer(listing)
        return Response(serializer.data)


class ListingCreateView(generics.CreateAPIView):
    """Create new listing."""
    
    serializer_class = ListingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create listing."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        listing = serializer.save()
        
        # Log activity
        log_user_activity(
            user=request.user,
            activity_type='listing_created',
            description=f'Created listing: {listing.title}',
            metadata={'listing_id': str(listing.id)},
            request=request
        )
        
        # Return detailed listing data
        detail_serializer = ListingDetailSerializer(listing, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class ListingUpdateView(generics.UpdateAPIView):
    """Update listing."""
    
    queryset = Listing.objects.all()
    serializer_class = ListingUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to update their own listings."""
        return self.queryset.filter(seller=self.request.user)


class ListingDeleteView(generics.DestroyAPIView):
    """Delete listing."""
    
    queryset = Listing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow users to delete their own listings."""
        return self.queryset.filter(seller=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete listing."""
        listing = self.get_object()
        
        # Log activity
        log_user_activity(
            user=request.user,
            activity_type='listing_deleted',
            description=f'Deleted listing: {listing.title}',
            metadata={'listing_id': str(listing.id)},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)


class UserListingsView(generics.ListAPIView):
    """Get user's listings."""
    
    serializer_class = ListingBasicSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get current user's listings."""
        return Listing.objects.filter(
            seller=self.request.user
        ).select_related('category').prefetch_related('images').order_by('-created_at')


class HotDealsView(generics.ListAPIView):
    """Get hot deals."""
    
    queryset = Listing.objects.filter(
        status='active',
        is_hot_deal=True,
        original_price__isnull=False,
        discount_percentage__isnull=False
    ).select_related('seller', 'category').prefetch_related('images')
    serializer_class = HotDealSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get hot deals ordered by discount percentage."""
        return self.queryset.order_by('-discount_percentage', '-created_at')[:10]


class FeaturedListingsView(generics.ListAPIView):
    """Get featured listings for homepage."""
    
    queryset = Listing.objects.filter(
        status='active',
        is_featured=True
    ).select_related('seller', 'category').prefetch_related('images')
    serializer_class = ListingBasicSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get featured listings."""
        return self.queryset.order_by('-created_at')[:6]


class PremiumListingsView(generics.ListAPIView):
    """Get premium listings."""
    
    queryset = Listing.objects.filter(
        status='active',
        is_premium=True
    ).select_related('seller', 'category').prefetch_related('images')
    serializer_class = ListingBasicSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get premium listings."""
        return self.queryset.order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def contact_seller(request, listing_id):
    """Contact seller."""
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Don't allow contacting own listings
    if listing.seller == request.user:
        return Response(
            {'error': 'Cannot contact yourself'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ListingContactSerializer(
        data=request.data,
        context={'request': request, 'listing': listing}
    )
    serializer.is_valid(raise_exception=True)
    contact = serializer.save()
    
    # Log activity
    log_user_activity(
        user=request.user,
        activity_type='seller_contacted',
        description=f'Contacted seller for: {listing.title}',
        metadata={
            'listing_id': str(listing.id),
            'contact_type': contact.contact_type
        },
        request=request
    )
    
    return Response({
        'message': 'Contact recorded successfully',
        'seller_phone': listing.seller.phone_number.as_e164 if listing.seller.profile.show_phone else None,
        'seller_whatsapp': listing.seller.profile.whatsapp if listing.seller.profile.whatsapp else None
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def report_listing(request, listing_id):
    """Report listing."""
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ListingReportSerializer(
        data=request.data,
        context={'request': request, 'listing': listing}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({'message': 'Report submitted successfully'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_suggestions(request):
    """Get search suggestions."""
    query = request.query_params.get('q', '').strip()
    
    if len(query) < 2:
        return Response([])
    
    # Get title suggestions
    title_suggestions = Listing.objects.filter(
        status='active',
        title__icontains=query
    ).values_list('title', flat=True).distinct()[:5]
    
    # Get category suggestions
    category_suggestions = Category.objects.filter(
        is_active=True,
        name__icontains=query
    ).values_list('name', flat=True)[:3]
    
    suggestions = list(title_suggestions) + list(category_suggestions)
    
    return Response(suggestions[:8])


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def listing_stats(request):
    """Get general listing statistics."""
    stats = {
        'total_listings': Listing.objects.filter(status='active').count(),
        'premium_listings': Listing.objects.filter(status='active', is_premium=True).count(),
        'categories_count': Category.objects.filter(is_active=True).count(),
        'hot_deals_count': Listing.objects.filter(status='active', is_hot_deal=True).count(),
    }
    
    # Category breakdown
    category_stats = Category.objects.filter(is_active=True).annotate(
        listing_count=Count('listings', filter=Q(listings__status='active'))
    ).values('name', 'listing_count').order_by('-listing_count')[:10]
    
    stats['top_categories'] = list(category_stats)
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_sold(request, listing_id):
    """Mark listing as sold."""
    try:
        listing = Listing.objects.get(id=listing_id, seller=request.user)
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found or not owned by you'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    listing.status = 'sold'
    listing.save(update_fields=['status'])
    
    # Update seller's successful transactions
    request.user.successful_transactions += 1
    request.user.save(update_fields=['successful_transactions'])
    
    # Log activity
    log_user_activity(
        user=request.user,
        activity_type='listing_sold',
        description=f'Marked listing as sold: {listing.title}',
        metadata={'listing_id': str(listing.id)},
        request=request
    )
    
    return Response({'message': 'Listing marked as sold'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reactivate_listing(request, listing_id):
    """Reactivate expired listing (premium only)."""
    try:
        listing = Listing.objects.get(id=listing_id, seller=request.user)
    except Listing.DoesNotExist:
        return Response(
            {'error': 'Listing not found or not owned by you'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if listing.status != 'expired':
        return Response(
            {'error': 'Only expired listings can be reactivated'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not listing.is_premium:
        return Response(
            {'error': 'Only premium listings can be reactivated'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    listing.status = 'active'
    listing.save(update_fields=['status'])
    
    return Response({'message': 'Listing reactivated successfully'})