from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('writings/', views.WritingsView.as_view(), name='writings'),
    path('writings/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),
    path('cv/', views.CVView.as_view(), name='cv'),
    path('labs/', views.LabsView.as_view(), name='labs'),
    path('labs/<slug:slug>/', views.LabDetailView.as_view(), name='lab-detail'),
]
