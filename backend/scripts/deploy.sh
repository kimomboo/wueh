#!/bin/bash
# Deployment script for PeerStorm Nexus Arena

echo "🚀 Deploying PeerStorm Nexus Arena Backend..."

# Set environment
export DJANGO_SETTINGS_MODULE=peerstorm.settings.production

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@peerstorm.com',
        password='admin123',
        full_name='Admin User',
        phone_number='+254712345678',
        location='Nairobi'
    )
    print("Superuser created")
else:
    print("Superuser already exists")
EOF

# Load initial data
echo "📊 Loading initial data..."
python manage.py loaddata initial_data.json || echo "Initial data loading skipped"

echo "✅ Deployment completed successfully!"