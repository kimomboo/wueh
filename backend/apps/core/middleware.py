"""
Custom middleware for PeerStorm Nexus Arena.
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """Custom security middleware."""
    
    def process_request(self, request):
        """Process incoming request for security checks."""
        # Add security headers
        pass
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Add CORS headers for API requests
        if request.path.startswith('/api/'):
            response['Access-Control-Allow-Origin'] = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Allow-Credentials'] = 'true'
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log API requests for monitoring."""
    
    def process_request(self, request):
        """Log incoming API requests."""
        if request.path.startswith('/api/') and settings.DEBUG:
            logger.info(f"API Request: {request.method} {request.path}")
        
        return None


class RateLimitMiddleware(MiddlewareMixin):
    """Simple rate limiting middleware."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_counts = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        """Check rate limits for API requests."""
        if not request.path.startswith('/api/'):
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Simple rate limiting (100 requests per minute)
        import time
        current_time = int(time.time() / 60)  # Current minute
        
        if ip not in self.request_counts:
            self.request_counts[ip] = {}
        
        if current_time not in self.request_counts[ip]:
            self.request_counts[ip][current_time] = 0
        
        self.request_counts[ip][current_time] += 1
        
        # Clean old entries
        for minute in list(self.request_counts[ip].keys()):
            if minute < current_time - 5:  # Keep last 5 minutes
                del self.request_counts[ip][minute]
        
        # Check limit
        if self.request_counts[ip][current_time] > 100:
            return JsonResponse(
                {'error': 'Rate limit exceeded. Please try again later.'},
                status=429
            )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip