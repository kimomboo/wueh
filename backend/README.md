# PeerStorm Nexus Arena Backend

A robust Django REST API backend for Kenya's premier peer-to-peer marketplace.

## 🚀 Features

- **User Authentication**: JWT-based auth with phone/email validation
- **Listing Management**: Full CRUD with image uploads and categorization
- **Payment Integration**: M-PESA Daraja API with STK Push
- **Real-time Notifications**: WebSocket support for live updates
- **Analytics**: Comprehensive tracking and reporting
- **Admin Dashboard**: Full content management system

## 🛠️ Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL with Redis caching
- **Storage**: Cloudinary for images
- **Email**: Resend service
- **Payments**: Safaricom M-PESA Daraja API
- **Task Queue**: Celery with Redis broker
- **Real-time**: Django Channels with WebSocket

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Git

## 🔧 Local Development Setup

1. **Clone and setup**:
```bash
git clone <repository-url>
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run setup script**:
```bash
python scripts/setup_local.py
```

3. **Update environment variables**:
Edit `.env` file with your API keys:
- Cloudinary credentials
- Resend API key
- M-PESA credentials

4. **Start services**:
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A peerstorm worker --loglevel=info

# Terminal 3: Celery Beat (optional)
celery -A peerstorm beat --loglevel=info

# Terminal 4: Django Server
python manage.py runserver
```

## 🌐 Production Deployment

### Render Deployment

1. **Connect Repository**: Link your GitHub repo to Render
2. **Environment Variables**: Set all required env vars in Render dashboard
3. **Deploy**: Render will automatically deploy using `render.yaml`

### Manual Deployment

```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=peerstorm.settings.production

# Run deployment script
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 📊 API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update profile

### Listings
- `GET /api/listings/` - List all listings
- `POST /api/listings/create/` - Create listing
- `GET /api/listings/{id}/` - Get listing details
- `PUT /api/listings/{id}/update/` - Update listing
- `DELETE /api/listings/{id}/delete/` - Delete listing

### Categories
- `GET /api/listings/categories/` - List categories
- `GET /api/listings/hot-deals/` - Get hot deals
- `GET /api/listings/featured/` - Get featured listings

### Payments
- `GET /api/payments/plans/` - Get premium plans
- `POST /api/payments/create/` - Create payment
- `GET /api/payments/` - List user payments
- `POST /api/payments/mpesa/callback/` - M-PESA callback

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/read/` - Mark as read
- `GET /api/notifications/unread-count/` - Get unread count

## 🔐 Environment Variables

### Required for Production
```env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Resend
RESEND_API_KEY=your-resend-key
DEFAULT_FROM_EMAIL=noreply@peerstorm.com

# M-PESA
MPESA_ENVIRONMENT=production
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://seraphically.onrender.com/api/payments/mpesa/callback/

# Frontend
FRONTEND_URL=https://newrevolution.netlify.app
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Monitoring

### Health Check
- `GET /health/` - API health status

### Admin Dashboard
- Access: `/admin/`
- Default credentials: `admin/admin123` (change in production)

### Analytics
- `GET /api/analytics/dashboard/` - Admin analytics
- `GET /api/analytics/user/` - User analytics

## 🔄 Background Tasks

### Celery Tasks
- **Expire Free Ads**: Runs hourly to expire 4-day old free ads
- **Send Notifications**: Email and push notifications
- **Generate Analytics**: Daily statistics generation
- **Cleanup**: Remove old data and optimize database

### Monitoring Celery
```bash
# Monitor tasks
celery -A peerstorm events

# Flower (web monitoring)
pip install flower
celery -A peerstorm flower
```

## 🛡️ Security Features

- **CORS**: Configured for frontend domain
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM safety
- **XSS Protection**: Content sanitization
- **CSRF Protection**: Token-based protection

## 📱 M-PESA Integration

### STK Push Flow
1. User initiates payment
2. Backend calls Daraja API
3. User receives STK push
4. User enters M-PESA PIN
5. Callback confirms payment
6. Listing upgraded to premium

### Testing M-PESA
Use Safaricom sandbox credentials for testing:
- Test phone: `254708374149`
- Test amount: Any amount
- PIN: `1234`

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **Redis Connection Error**:
   - Start Redis server: `redis-server`
   - Check Redis URL in settings

3. **M-PESA Callback Issues**:
   - Ensure callback URL is accessible
   - Check Safaricom whitelist
   - Verify SSL certificate

4. **Email Not Sending**:
   - Check Resend API key
   - Verify email templates exist
   - Check Celery worker is running

### Logs
```bash
# View Django logs
tail -f logs/django.log

# View Celery logs
celery -A peerstorm worker --loglevel=debug
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is proprietary software for PeerStorm Nexus Arena.

## 📞 Support

For technical support, contact the development team or create an issue in the repository.