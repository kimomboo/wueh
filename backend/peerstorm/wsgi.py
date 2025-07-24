"""
WSGI config for PeerStorm Nexus Arena project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peerstorm.settings.production')

application = get_wsgi_application()