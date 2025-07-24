"""
Production settings for PeerStorm Nexus Arena.
"""
from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'seraphically.onrender.com',
    '.onrender.com',
    'newrevolution.netlify.app',
    '.netlify.app',
]

# CORS Configuration for production
CORS_ALLOWED_ORIGINS = [
    "https://newrevolution.netlify.app",
    "https://seraphically.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

# Database for production (Render PostgreSQL)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# M-PESA Configuration for production
MPESA_ENVIRONMENT = 'production'
MPESA_CALLBACK_URL = 'https://seraphically.onrender.com/api/payments/mpesa/callback/'

# Production logging
LOGGING['handlers']['file']['filename'] = '/tmp/django.log'
LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['peerstorm']['level'] = 'INFO'

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'