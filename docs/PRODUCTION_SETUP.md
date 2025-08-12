# Production Deployment Configuration

## Environment Variables Setup

### Required for Production

Copy `.env.production` to `.env` and update the following critical values:

```bash
# Security - CRITICAL: Change these values
DEBUG=False
DJANGO_SECRET_KEY=your-long-random-secret-key-here

# Domain Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration (choose one)
# Option 1: DATABASE_URL (recommended for Render, Heroku, etc.)
DATABASE_URL=postgresql://user:password@host:port/database

# Option 2: Individual database settings
DB_NAME=your_production_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# HTTPS/SSL Settings (automatically enabled in production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

### CSRF Trusted Origins

Update the CSRF_TRUSTED_ORIGINS in `sk/settings.py` with your actual domains:

```python
# Production domains - Update these with your actual domains
if not DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'https://yourdomain.com',
        'https://www.yourdomain.com',
        # Add your actual production domains here
    ])
```

## Security Features

### Automatically Enabled in Production (DEBUG=False):
- SSL redirect (`SECURE_SSL_REDIRECT=True`)
- HSTS headers with 1-year max-age
- Secure cookies for sessions and CSRF
- Referrer policy: `strict-origin-when-cross-origin`
- Cross-origin opener policy: `same-origin`

### Database Security:
- PostgreSQL with connection timeout (10 seconds)
- SQLite fallback disabled in production
- Proper connection pooling support

### Static Files:
- WhiteNoise with compressed manifest storage
- Optimized for production serving
- `WHITENOISE_USE_FINDERS=False` in production

## Deployment Checklist

### Before Deployment:
1. [ ] Update `DJANGO_SECRET_KEY` with a secure random value
2. [ ] Set `DEBUG=False`
3. [ ] Configure `ALLOWED_HOSTS` with your domain(s)
4. [ ] Update `CSRF_TRUSTED_ORIGINS` with your domain(s)
5. [ ] Set up PostgreSQL database or configure `DATABASE_URL`
6. [ ] Ensure SSL certificate is configured on your hosting platform

### After Deployment:
1. [ ] Run migrations: `python manage.py migrate`
2. [ ] Collect static files: `python manage.py collectstatic`
3. [ ] Create superuser: `python manage.py createsuperuser`
4. [ ] Test admin login functionality
5. [ ] Verify SSL is working correctly
6. [ ] Test CSRF protection on forms

## Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `SECURE_SSL_REDIRECT` | `False` | `True` |
| Database | SQLite | PostgreSQL |
| CSRF Origins | HTTP + HTTPS | HTTPS only |
| Static Files | With finders | Compressed manifest |

## Common Issues

### CSRF Verification Failed
- Ensure your domain is in `CSRF_TRUSTED_ORIGINS`
- Verify SSL is properly configured
- Check that `CSRF_COOKIE_SECURE=True` in production

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Ensure WhiteNoise is properly configured
- Check `STATIC_ROOT` and `STATIC_URL` settings

### Database Connection Issues
- Verify `DATABASE_URL` format
- Check PostgreSQL server is running
- Ensure connection credentials are correct
