from django.urls import path, re_path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

LEGACY_REDIRECT_PATHS = ('cv', 'labs', 'about', 'writing', 'writings', 'notes')

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('notes/<slug:slug>/', views.NoteDetailView.as_view(), name='note-detail'),
    *(
        path(f'{slug}/', RedirectView.as_view(pattern_name='core:home', permanent=False), name=slug)
        for slug in LEGACY_REDIRECT_PATHS
    ),
    *(
        re_path(rf'^{slug}/.+$', RedirectView.as_view(pattern_name='core:home', permanent=False))
        for slug in LEGACY_REDIRECT_PATHS if slug != 'notes'
    ),
]
