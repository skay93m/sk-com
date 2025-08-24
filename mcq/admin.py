from django.contrib import admin
from .models import MCQ, Choice, ReviewSchedule, Topic

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_mcq_count', 'color', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

@admin.register(MCQ)
class MCQAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'difficulty', 'get_topics', 'created_at']
    list_filter = ['difficulty', 'topics', 'created_at']
    search_fields = ['question_text']
    filter_horizontal = ['topics']
    readonly_fields = ['created_at', 'updated_at']
    
    def question_text_short(self, obj):
        return obj.question_text[:80] + "..." if len(obj.question_text) > 80 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def get_topics(self, obj):
        return ", ".join([topic.name for topic in obj.topics.all()])
    get_topics.short_description = 'Topics'

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'mcq', 'is_correct']
    list_filter = ['is_correct', 'mcq__difficulty']
    search_fields = ['text', 'mcq__question_text']
    
    def text_short(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
    text_short.short_description = 'Choice Text'

@admin.register(ReviewSchedule)
class ReviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['mcq_short', 'srs_stage', 'next_review', 'total_reviews', 'consecutive_correct']
    list_filter = ['srs_stage', 'next_review']
    search_fields = ['mcq__question_text']
    readonly_fields = ['total_reviews', 'consecutive_correct']
    
    def mcq_short(self, obj):
        return obj.mcq.question_text[:50] + "..." if len(obj.mcq.question_text) > 50 else obj.mcq.question_text
    mcq_short.short_description = 'Question'
