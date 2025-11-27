from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.PortfolioView.as_view(), name='portfolio'),
    path('<str:identity>/', views.IdentityDetailView.as_view(), name='identity-detail'),
]