from django.urls import path
from .views_quiz import mcq_landing, study, practice, stats, topic_selection, manage_topics
from .views_author import create_mcq, mcq_list, edit_mcq, delete_mcq

app_name = 'mcq'
urlpatterns = [
    path("", mcq_landing, name="landing"),
    path("study/", study, name="study"),
    path("practice/", practice, name="practice"),
    path("topics/", topic_selection, name="topic_selection"),
    path("topics/manage/", manage_topics, name="manage_topics"),
    path("stats/", stats, name="stats"),
    path("new/", create_mcq, name="create_mcq"),
    path("list/", mcq_list, name="mcq_list"),
    path("edit/<int:mcq_id>/", edit_mcq, name="edit_mcq"),
    path("delete/<int:mcq_id>/", delete_mcq, name="delete_mcq"),
]