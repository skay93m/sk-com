"""
URL configuration for sk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import SecureAdminLoginView, SecureAdminLogoutView

urlpatterns = [
    path('secure-admin-login/', SecureAdminLoginView.as_view(), name='secure_admin_login'),
    path('secure-admin-logout/', SecureAdminLogoutView.as_view(), name='secure_admin_logout'),
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('projects/', include('projects.urls')),
    path('writing/', include('writing.urls')),
    path('cv/', include('cv.urls')),
    path('mcq/', include('mcq.urls')),
]

# Serve static files in development and production
# This ensures static files are properly served regardless of DEBUG setting
if settings.DEBUG or settings.WHITENOISE_USE_FINDERS:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Also include STATICFILES_DIRS for development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
