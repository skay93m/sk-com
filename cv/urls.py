from django import urls
from . import views

app_name = 'cv'
urlpatterns = [
    urls.path('', views.cv_main, name='cv_main'),
]