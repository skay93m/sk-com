# Static Files Configuration with Whitenoise

This guide explains the static files setup using Whitenoise for serving static files in both development and production.

## Overview

Whitenoise allows your Django application to serve its own static files without requiring a separate web server like Nginx or Apache. This simplifies deployment and reduces infrastructure complexity.

## Configuration

### Middleware Setup
Whitenoise is configured as middleware in `settings.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
    # ... other middleware
]
```

### Static Files Settings

```python
# Static file serving
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Static file directories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'sk', 'static'),
    os.path.join(BASE_DIR, 'home', 'static'),
]

# Whitenoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
```

## Features Enabled

### 1. Compressed Static Files
- **Gzip Compression**: Automatically compresses CSS, JS, and other static files
- **Brotli Compression**: Uses Brotli compression when available for better compression ratios
- **Automatic Detection**: Serves compressed versions to compatible browsers

### 2. Manifest Static Files
- **File Hashing**: Adds unique hashes to filenames for cache busting
- **Cache Headers**: Sets appropriate cache headers for optimal performance
- **Version Management**: Handles file versioning automatically

### 3. Development Features
- **WHITENOISE_USE_FINDERS**: Allows serving files directly from source in development
- **WHITENOISE_AUTOREFRESH**: Automatically refreshes static files during development

## Usage

### Development
Static files are served automatically during development:

```bash
# Start development server
python manage.py runserver

# Static files are served at: http://localhost:8000/static/
```

### Production
Static files are collected and served efficiently:

```bash
# Collect static files (done automatically in Docker build)
python manage.py collectstatic --noinput

# Files are served from /staticfiles/ directory
```

## File Structure

```
sk-com/
├── sk/
│   └── static/           # Project-level static files
│       ├── css/
│       ├── js/
│       └── images/
├── home/
│   └── static/           # App-level static files
│       └── home/
│           ├── css/
│           ├── js/
│           └── images/
└── staticfiles/          # Collected static files (production)
    ├── admin/            # Django admin static files
    ├── bootstrap5/       # Bootstrap static files
    └── staticfiles.json  # Whitenoise manifest
```

## Benefits

### Performance
- **CDN-like Performance**: Serves static files with optimal headers
- **Compression**: Reduces bandwidth usage with gzip/brotli compression
- **Caching**: Proper cache headers for browser caching
- **Manifest Storage**: Efficient file versioning and cache busting

### Simplicity
- **No External Dependencies**: No need for Nginx or Apache
- **Easy Deployment**: Works on any platform (Render, Heroku, etc.)
- **Configuration-Free**: Works out of the box with minimal setup

### Security
- **Secure Headers**: Proper security headers for static files
- **HTTPS Support**: Full HTTPS support for static file serving
- **Content-Type Detection**: Proper MIME type detection

## Environment-Specific Behavior

### Development (`DEBUG=True`)
- Uses `WHITENOISE_USE_FINDERS` to serve files from source
- Enables `WHITENOISE_AUTOREFRESH` for live reloading
- No compression to speed up development

### Production (`DEBUG=False`)
- Serves files from `STATIC_ROOT` (collected files)
- Enables compression and caching
- Optimized for performance

## Deployment

### Dockerfile
The Dockerfile automatically collects static files during build:

```dockerfile
# Collect static files during build
RUN .venv/bin/python manage.py collectstatic --noinput
```

### Render Deployment
The `render.yaml` includes static file collection in the build command:

```yaml
buildCommand: ".venv/bin/python manage.py collectstatic --noinput"
```

## Troubleshooting

### Common Issues

1. **Static files not loading**:
   ```bash
   # Check if static files are collected
   python manage.py collectstatic --noinput
   
   # Verify STATIC_ROOT directory exists
   ls -la staticfiles/
   ```

2. **Missing CSS/JS files**:
   ```bash
   # Check static file directories
   python manage.py findstatic bootstrap5/css/bootstrap.min.css
   ```

3. **Compression not working**:
   - Ensure `STATICFILES_STORAGE` is set correctly
   - Check that files are being processed during collection

### Useful Commands

```bash
# Collect static files
python manage.py collectstatic --noinput

# Find static file location
python manage.py findstatic filename.css

# Check static files configuration
python manage.py check --deploy

# Clear collected static files
rm -rf staticfiles/
python manage.py collectstatic --noinput
```

## Advanced Configuration

### Custom Headers
You can add custom headers in settings.py:

```python
WHITENOISE_EXTRA_HEADERS = {
    '*.css': ('Cache-Control', 'max-age=31536000'),
    '*.js': ('Cache-Control', 'max-age=31536000'),
    '*.woff2': ('Cache-Control', 'max-age=31536000'),
}
```

### Skip Compression
To skip compression for specific files:

```python
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']
```

Your static files are now configured for optimal performance in both development and production environments!
