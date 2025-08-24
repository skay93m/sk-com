from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model"""
    
    list_display = ['title', 'category', 'description_short', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def description_short(self, obj):
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description
    description_short.short_description = 'Description'
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'category', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
