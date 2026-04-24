from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import RobotsTxtView

urlpatterns = [
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG or settings.WHITENOISE_USE_FINDERS:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
