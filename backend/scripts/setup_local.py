#!/usr/bin/env python
"""
Local development setup script for PeerStorm Nexus Arena.
"""
import os
import sys
import subprocess
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peerstorm.settings.local')

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False

def setup_database():
    """Set up local PostgreSQL database."""
    print("\n📊 Setting up PostgreSQL database...")
    
    # Check if PostgreSQL is running
    try:
        subprocess.run(['psql', '--version'], check=True, capture_output=True)
        print("✅ PostgreSQL is installed")
    except subprocess.CalledProcessError:
        print("❌ PostgreSQL is not installed. Please install PostgreSQL first.")
        return False
    
    # Create database and user
    commands = [
        "createdb peerstorm_local",
        "psql -d peerstorm_local -c \"CREATE USER postgres WITH PASSWORD 'password';\"",
        "psql -d peerstorm_local -c \"GRANT ALL PRIVILEGES ON DATABASE peerstorm_local TO postgres;\""
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Database might already exist, continue
            pass
    
    return True

def setup_django():
    """Set up Django application."""
    django.setup()
    
    # Run migrations
    if not run_command('python manage.py makemigrations', 'Creating migrations'):
        return False
    
    if not run_command('python manage.py migrate', 'Running migrations'):
        return False
    
    # Create superuser
    print("\n👤 Creating superuser...")
    try:
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
            print("✅ Superuser created (admin/admin123)")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False
    
    # Load initial data
    if not run_command('python manage.py loaddata initial_data.json', 'Loading initial data'):
        print("⚠️ Initial data loading failed (this is optional)")
    
    return True

def setup_redis():
    """Check Redis setup."""
    print("\n🔴 Checking Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        print("Redis is optional for local development")
        return True

def create_env_file():
    """Create .env file for local development."""
    env_file = backend_dir / '.env'
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("\n📝 Creating .env file...")
    
    env_content = """# Django Settings
SECRET_KEY=django-insecure-local-development-key-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=peerstorm.settings.local

# Database Configuration
DB_NAME=peerstorm_local
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Cloudinary Configuration (Get from cloudinary.com)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email Configuration (Get from resend.com)
RESEND_API_KEY=your-resend-api-key
DEFAULT_FROM_EMAIL=noreply@peerstorm.com

# M-PESA Configuration (Get from Safaricom Developer Portal)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=http://localhost:8000/api/payments/mpesa/callback/

# Frontend URL
FRONTEND_URL=http://localhost:5173
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️ Please update the .env file with your actual API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up PeerStorm Nexus Arena Backend for Local Development")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Setup Django
    if not setup_django():
        return False
    
    # Check Redis
    setup_redis()
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys (Cloudinary, Resend, M-PESA)")
    print("2. Start Redis server: redis-server")
    print("3. Start Celery worker: celery -A peerstorm worker --loglevel=info")
    print("4. Start Django server: python manage.py runserver")
    print("5. Access admin at: http://localhost:8000/admin/ (admin/admin123)")
    print("6. API docs at: http://localhost:8000/api/")
    
    return True

if __name__ == '__main__':
    main()