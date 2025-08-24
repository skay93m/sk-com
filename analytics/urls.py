"""
Analytics URL configuration.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('api/data/', views.analytics_api_data, name='api_data'),
    path('export/', views.export_analytics, name='export'),
]
