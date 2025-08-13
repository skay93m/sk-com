from django.contrib import admin
from .models import Writing

@admin.register(Writing)
class WritingAdmin(admin.ModelAdmin):
    """Admin interface for Writing model"""
    
    list_display = ['title', 'author', 'writing_type', 'status', 'featured', 'created_at', 'published_at']
    list_filter = ['writing_type', 'status', 'featured', 'created_at', 'published_at']
    search_fields = ['title', 'content', 'tags', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'writing_type')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set author to current user if not set"""
        if not change and not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
