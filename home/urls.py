from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hero/', views.hero, name='hero'),
    path('hero/new/', views.hero_form, name='hero_form'),
]
