"""
Celery configuration for PeerStorm Nexus Arena.
"""
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peerstorm.settings.local')

app = Celery('peerstorm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'expire-free-ads': {
        'task': 'apps.listings.tasks.expire_free_ads',
        'schedule': 3600.0,  # Run every hour
    },
    'cleanup-expired-listings': {
        'task': 'apps.listings.tasks.cleanup_expired_listings',
        'schedule': 86400.0,  # Run daily
    },
    'send-expiry-notifications': {
        'task': 'apps.notifications.tasks.send_expiry_notifications',
        'schedule': 3600.0,  # Run every hour
    },
}

app.conf.timezone = 'Africa/Nairobi'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')