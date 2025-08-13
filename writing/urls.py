from django.urls import path
from . import views

app_name = 'writing'

urlpatterns = [
    path('', views.writing_list, name='writing_list'),
    path('create/', views.writing_create, name='writing_create'),
    path('<int:pk>/', views.writing_detail, name='writing_detail'),
    path('<int:pk>/edit/', views.writing_edit, name='writing_edit'),
    path('<int:pk>/delete/', views.writing_delete, name='writing_delete'),
]
