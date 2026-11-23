from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

LEGACY_REDIRECT_PATHS = ('cv', 'labs', 'about', 'writing')

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('writings/', views.WritingsView.as_view(), name='writings'),
    path('writings/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    *(
        path(f'{slug}/', RedirectView.as_view(pattern_name='core:home', permanent=False), name=slug)
        for slug in LEGACY_REDIRECT_PATHS
    ),
    path('labs/<slug:slug>/', views.LabDetailView.as_view(), name='lab-detail'),
]
