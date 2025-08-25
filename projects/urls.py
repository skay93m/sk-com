from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project URLs
    path('', views.project_list, name='project_list'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('new/', views.project_create, name='project_create'),
    path('new/from-template/', views.project_create_from_template, name='project_create_from_template'),
    path('template/download/', views.project_template_download, name='project_template_download'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Milestone URLs
    path('<int:pk>/milestones/<int:milestone_pk>/edit/', views.milestone_edit, name='milestone_edit'),
    path('<int:pk>/milestones/<int:milestone_pk>/delete/', views.milestone_delete, name='milestone_delete'),
    path('<int:pk>/milestones/<int:milestone_pk>/toggle-complete/', views.milestone_toggle_complete, name='milestone_toggle_complete'),
    
    # Task URLs
    path('<int:pk>/tasks/<int:task_pk>/edit/', views.task_edit, name='task_edit'),
    path('<int:pk>/tasks/<int:task_pk>/delete/', views.task_delete, name='task_delete'),
    path('<int:pk>/tasks/<int:task_pk>/update-status/', views.task_update_status, name='task_update_status'),
]