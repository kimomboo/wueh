"""
Core utilities for PeerStorm Nexus Arena.
"""
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_activity(user, activity_type, description, metadata=None, request=None):
    """Log user activity."""
    from apps.accounts.models import UserActivity
    
    try:
        activity_data = {
            'user': user,
            'activity_type': activity_type,
            'description': description,
            'metadata': metadata or {}
        }
        
        if request:
            activity_data.update({
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
            })
        
        UserActivity.objects.create(**activity_data)
        
    except Exception as e:
        logger.error(f"Failed to log user activity: {e}")


def send_real_time_notification(user_id, notification_data):
    """Send real-time notification via WebSocket."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    'type': 'notification_message',
                    'notification': notification_data
                }
            )
    except Exception as e:
        logger.error(f"Failed to send real-time notification: {e}")


def format_kenyan_phone(phone_number):
    """Format phone number to Kenyan standard."""
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Convert to international format
    if phone.startswith('07') or phone.startswith('01'):
        return f"254{phone[1:]}"
    elif phone.startswith('254'):
        return phone
    elif phone.startswith('7') or phone.startswith('1'):
        return f"254{phone}"
    
    return phone


def validate_kenyan_phone(phone_number):
    """Validate Kenyan phone number format."""
    formatted = format_kenyan_phone(phone_number)
    
    # Check if it's a valid Kenyan mobile number
    if len(formatted) != 12:
        return False
    
    if not formatted.startswith('254'):
        return False
    
    # Check if it's a mobile number (7xx or 1xx after 254)
    if not (formatted[3] in ['7', '1']):
        return False
    
    return True


def generate_listing_slug(title):
    """Generate unique slug for listing."""
    from django.utils.text import slugify
    from apps.listings.models import Listing
    
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while Listing.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def calculate_listing_score(listing):
    """Calculate listing relevance score for search."""
    score = 0
    
    # Premium listings get higher score
    if listing.is_premium:
        score += 100
    
    # Featured listings get boost
    if listing.is_featured:
        score += 50
    
    # Recent listings get boost
    days_old = (timezone.now() - listing.created_at).days
    if days_old <= 1:
        score += 30
    elif days_old <= 7:
        score += 20
    elif days_old <= 30:
        score += 10
    
    # High engagement gets boost
    score += min(listing.views / 10, 20)  # Max 20 points from views
    score += min(listing.favorites_count * 5, 25)  # Max 25 points from favorites
    
    # Verified seller gets boost
    if listing.seller.is_verified:
        score += 15
    
    return int(score)


def get_trending_categories():
    """Get trending categories based on recent activity."""
    from apps.listings.models import Category, Listing
    from django.db.models import Count
    from datetime import timedelta
    
    # Get categories with most listings in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    
    trending = Category.objects.filter(
        listings__created_at__gte=week_ago,
        listings__status='active'
    ).annotate(
        recent_count=Count('listings')
    ).order_by('-recent_count')[:10]
    
    return trending


def clean_search_query(query):
    """Clean and prepare search query."""
    if not query:
        return ""
    
    # Remove special characters but keep spaces and hyphens
    import re
    cleaned = re.sub(r'[^\w\s\-]', '', query)
    
    # Remove extra spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


def get_location_suggestions(query):
    """Get location suggestions based on query."""
    if not query or len(query) < 2:
        return []
    
    # Filter Kenyan counties that match the query
    matching_counties = [
        county for county in settings.KENYAN_COUNTIES
        if query.lower() in county.lower()
    ]
    
    return matching_counties[:5]


def get_price_range_suggestions():
    """Get common price ranges for filtering."""
    return [
        {'label': 'Under 10K', 'min': 0, 'max': 10000},
        {'label': '10K - 50K', 'min': 10000, 'max': 50000},
        {'label': '50K - 100K', 'min': 50000, 'max': 100000},
        {'label': '100K - 500K', 'min': 100000, 'max': 500000},
        {'label': '500K - 1M', 'min': 500000, 'max': 1000000},
        {'label': 'Above 1M', 'min': 1000000, 'max': None},
    ]


def sanitize_html(content):
    """Sanitize HTML content to prevent XSS."""
    import bleach
    
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    allowed_attributes = {}
    
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes)


def compress_image(image_file, max_size_mb=5):
    """Compress image if it's too large."""
    from PIL import Image
    import io
    
    if image_file.size <= max_size_mb * 1024 * 1024:
        return image_file
    
    # Open and compress image
    img = Image.open(image_file)
    
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    # Calculate new dimensions
    max_dimension = 1920
    if max(img.size) > max_dimension:
        ratio = max_dimension / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save compressed image
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    
    return output