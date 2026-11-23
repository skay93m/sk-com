from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('writings/', views.WritingsView.as_view(), name='writings'),
    path('writings/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('about/', RedirectView.as_view(url='/', permanent=False), name='about'),
    path('writing/', RedirectView.as_view(url='/', permanent=False), name='writing'),
    path('cv/', RedirectView.as_view(url="/", permanent=False), name='cv'),
    path('labs/', RedirectView.as_view(url="/", permanent=False), name='labs'),
    path('labs/<slug:slug>/', views.LabDetailView.as_view(), name='lab-detail'),
]
