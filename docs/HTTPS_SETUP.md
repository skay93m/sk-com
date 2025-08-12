# HTTPS Setup Guide

This guide will help you configure HTTPS for your Django application in different environments.

## Configuration Overview

The application includes comprehensive HTTPS security settings that can be controlled via environment variables:

### Environment Variables

| Variable | Description | Production Value | Development Value |
|----------|-------------|------------------|-------------------|
| `SECURE_SSL_REDIRECT` | Redirects all HTTP requests to HTTPS | `True` | `False` |
| `SECURE_HSTS_SECONDS` | HSTS max-age in seconds | `31536000` (1 year) | `0` |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `True` | `False` |
| `SECURE_HSTS_PRELOAD` | Enable HSTS preload | `True` | `False` |
| `SESSION_COOKIE_SECURE` | Send session cookies over HTTPS only | `True` | `False` |
| `CSRF_COOKIE_SECURE` | Send CSRF cookies over HTTPS only | `True` | `False` |

## Production Deployment

### 1. Render (Recommended)

If you're deploying to Render:

1. **Environment Variables**: Set these in your Render service settings:
   ```
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   SECURE_HSTS_PRELOAD=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

2. **SSL Certificate**: Render automatically provides SSL certificates for custom domains.

3. **Custom Domain**: Add your domain in Render's dashboard and update DNS records.

### 2. Other Platforms (Heroku, Railway, etc.)

Similar setup - most modern platforms provide automatic SSL certificates.

## Local Development

### Option 1: HTTP Only (Default)
For local development, you can keep HTTPS disabled:
```bash
# Don't set the HTTPS environment variables or set them to False
export SECURE_SSL_REDIRECT=False
```

### Option 2: Local HTTPS with django-extensions
If you need to test HTTPS locally:

1. Install django-extensions:
   ```bash
   uv add django-extensions
   ```

2. Add to `INSTALLED_APPS` in settings.py:
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'django_extensions',
   ]
   ```

3. Run with SSL:
   ```bash
   python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
   ```

### Option 3: Local HTTPS with mkcert
1. Install mkcert: https://github.com/FiloSottile/mkcert
2. Create local certificates:
   ```bash
   mkcert -install
   mkcert localhost 127.0.0.1
   ```
3. Use with runserver_plus or nginx proxy

## Security Features Explained

### HSTS (HTTP Strict Transport Security)
- Forces browsers to use HTTPS for future visits
- `SECURE_HSTS_SECONDS`: Duration browsers remember the HSTS policy
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`: Applies to all subdomains
- `SECURE_HSTS_PRELOAD`: Allows inclusion in browser preload lists

### Secure Cookies
- `SESSION_COOKIE_SECURE`: Session cookies only sent over HTTPS
- `CSRF_COOKIE_SECURE`: CSRF protection cookies only sent over HTTPS

### Additional Security Headers
- `SECURE_CONTENT_TYPE_NOSNIFF`: Prevents MIME type sniffing
- `SECURE_BROWSER_XSS_FILTER`: Enables XSS filtering in browsers
- `X_FRAME_OPTIONS`: Prevents clickjacking attacks

## Testing HTTPS Configuration

1. **SSL Labs Test**: https://www.ssllabs.com/ssltest/
2. **Security Headers**: https://securityheaders.com/
3. **HSTS Preload**: https://hstspreload.org/

## Troubleshooting

### Common Issues:
1. **Redirect Loop**: Check `SECURE_PROXY_SSL_HEADER` is correctly set
2. **Mixed Content**: Ensure all resources (CSS, JS, images) use HTTPS
3. **Cookie Issues**: Verify secure cookie settings match your HTTPS setup

### Debug Commands:
```bash
# Check current settings
python manage.py shell -c "from django.conf import settings; print('SSL Redirect:', settings.SECURE_SSL_REDIRECT)"

# Test with curl
curl -I https://yourdomain.com
```
