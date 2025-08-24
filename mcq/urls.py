from django.urls import path
from .views_quiz import quiz
from .views_author import create_mcq, mcq_list, edit_mcq, delete_mcq

app_name = 'mcq'
urlpatterns = [
    path("", quiz, name="quiz"),
    path("new/", create_mcq, name="create_mcq"),
    path("list/", mcq_list, name="mcq_list"),
    path("edit/<int:mcq_id>/", edit_mcq, name="edit_mcq"),
    path("delete/<int:mcq_id>/", delete_mcq, name="delete_mcq"),
]