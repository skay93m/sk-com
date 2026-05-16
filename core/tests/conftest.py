import os

# Must be set before pytest-django initialises Django settings.
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-not-for-production")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ALLOWED_HOSTS", "localhost,127.0.0.1")
