from django.urls import path
from .views_quiz import mcq_landing, study, practice, stats, topic_selection, manage_topics
from .views_author import create_mcq, mcq_list, edit_mcq, delete_mcq
from .views_llm import (
    llm_generation_home, create_llm_prompt, paste_llm_response, 
    review_generated_questions, review_single_question, 
    finalize_generation_session, llm_generation_manual
)

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
    
    # LLM Generation URLs
    path("llm/", llm_generation_home, name="llm_generation_home"),
    path("llm/manual/", llm_generation_manual, name="llm_generation_manual"),
    path("llm/prompt/", create_llm_prompt, name="create_llm_prompt"),
    path("llm/response/<int:generation_id>/", paste_llm_response, name="llm_paste_response"),
    path("llm/review/<int:generation_id>/", review_generated_questions, name="review_generated_questions"),
    path("llm/review/question/<int:question_id>/", review_single_question, name="review_single_question"),
    path("llm/finalize/<int:generation_id>/", finalize_generation_session, name="finalize_generation_session"),
]