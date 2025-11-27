"""
URL configuration for sk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import RobotsTxtView

urlpatterns = [
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
]

# Serve static files in development and production
# This ensures static files are properly served regardless of DEBUG setting
if settings.DEBUG or settings.WHITENOISE_USE_FINDERS:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Also include STATICFILES_DIRS for development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
