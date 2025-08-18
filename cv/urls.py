from django import urls
from .views import cv_main, credential_list, credential_detail, credential_create, credential_edit, credential_delete

app_name = 'cv'
urlpatterns = [
    urls.path('', cv_main, name='cv_main'),
    urls.path('credential/', credential_list, name='credential_list'),
    urls.path('credential/<str:pk>', credential_detail, name='credential_detail'),
    urls.path('credential/new/', credential_create, name='credential_create'),
    urls.path('credential/<str:pk>/edit/', credential_edit, name='credential_edit'),
    urls.path('credential/<str:pk>/delete/', credential_delete, name='credential_delete'),    
]