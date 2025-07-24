"""
Core views for PeerStorm Nexus Arena.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import JsonResponse
from .models import SiteConfiguration, ContactMessage
from .utils import get_trending_categories, get_price_range_suggestions


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({
        'status': 'healthy',
        'service': 'PeerStorm Nexus Arena API',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def site_config(request):
    """Get site configuration."""
    configs = SiteConfiguration.objects.filter(is_active=True)
    
    config_dict = {}
    for config in configs:
        try:
            # Try to parse as JSON
            import json
            config_dict[config.key] = json.loads(config.value)
        except:
            # Keep as string if not valid JSON
            config_dict[config.key] = config.value
    
    return Response(config_dict)


@api_view(['GET'])
@permission_classes([AllowAny])
def app_constants(request):
    """Get application constants for frontend."""
    return Response({
        'kenyan_counties': settings.KENYAN_COUNTIES,
        'listing_categories': settings.LISTING_CATEGORIES,
        'premium_plans': settings.PREMIUM_PLANS,
        'free_ads_limit': settings.FREE_ADS_LIMIT,
        'free_ad_expiry_days': settings.FREE_AD_EXPIRY_DAYS,
        'price_ranges': get_price_range_suggestions(),
        'trending_categories': [
            {'name': cat.name, 'count': cat.recent_count}
            for cat in get_trending_categories()
        ]
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_us(request):
    """Handle contact form submissions."""
    required_fields = ['name', 'email', 'subject', 'message']
    
    for field in required_fields:
        if not request.data.get(field):
            return Response(
                {'error': f'{field.title()} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create contact message
    contact = ContactMessage.objects.create(
        name=request.data['name'],
        email=request.data['email'],
        phone=request.data.get('phone', ''),
        subject=request.data['subject'],
        message=request.data['message']
    )
    
    # Send notification to admin (async)
    from apps.notifications.tasks import send_contact_notification
    send_contact_notification.delay(contact.id)
    
    return Response({
        'message': 'Thank you for your message. We will get back to you soon!'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """Get search suggestions."""
    query = request.query_params.get('q', '').strip()
    
    if len(query) < 2:
        return Response([])
    
    suggestions = []
    
    # Get listing title suggestions
    from apps.listings.models import Listing
    title_suggestions = Listing.objects.filter(
        status='active',
        title__icontains=query
    ).values_list('title', flat=True).distinct()[:5]
    
    suggestions.extend(list(title_suggestions))
    
    # Get category suggestions
    from apps.listings.models import Category
    category_suggestions = Category.objects.filter(
        is_active=True,
        name__icontains=query
    ).values_list('name', flat=True)[:3]
    
    suggestions.extend(list(category_suggestions))
    
    # Get location suggestions
    from .utils import get_location_suggestions
    location_suggestions = get_location_suggestions(query)
    suggestions.extend(location_suggestions)
    
    # Remove duplicates and limit
    unique_suggestions = list(dict.fromkeys(suggestions))[:10]
    
    return Response(unique_suggestions)


def handler404(request, exception):
    """Custom 404 handler for API."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Endpoint not found',
            'status_code': 404
        }, status=404)
    
    # Let Django handle non-API 404s
    from django.http import Http404
    raise Http404


def handler500(request):
    """Custom 500 handler for API."""
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal server error',
            'status_code': 500
        }, status=500)
    
    # Let Django handle non-API 500s
    from django.http import HttpResponseServerError
    return HttpResponseServerError('Server Error')