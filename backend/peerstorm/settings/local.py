"""
Local development settings for PeerStorm Nexus Arena.
"""
from decouple import config
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS Configuration for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Only for development

# Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'peerstorm_db',
        'USER': 'peeruser',
        'PASSWORD': 'strongpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable HTTPS requirements for local development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# M-PESA Configuration for development (sandbox)
MPESA_ENVIRONMENT = 'sandbox'
MPESA_CALLBACK_URL = 'http://localhost:8000/api/payments/mpesa/callback/'

# Static files for development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Development-specific logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['peerstorm']['level'] = 'DEBUG'

# Django Extensions
if 'django_extensions' in INSTALLED_APPS:
    SHELL_PLUS_PRINT_SQL = True