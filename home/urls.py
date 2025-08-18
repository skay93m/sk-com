from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hero/', views.hero, name='hero'),
    path('hero/list/', views.hero_list, name='hero_list'),
    path('hero/new/', views.hero_form, name='hero_form'),
    path('hero/<int:hero_id>/delete/', views.hero_delete, name='hero_delete'),
]
