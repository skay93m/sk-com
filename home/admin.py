from django.contrib import admin
from .models import Hero, Expertise

@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    """Admin interface for Hero model"""
    
    list_display = ['header', 'tagline_short', 'cta', 'updated_at']
    search_fields = ['header', 'tagline', 'cta']
    readonly_fields = ['updated_at']
    date_hierarchy = 'updated_at'
    
    def tagline_short(self, obj):
        return obj.tagline[:50] + "..." if len(obj.tagline) > 50 else obj.tagline
    tagline_short.short_description = 'Tagline'
    
    fieldsets = (
        ('Hero Content', {
            'fields': ('header', 'tagline', 'cta')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    """Admin interface for Expertise model"""
    
    list_display = ['title', 'icon', 'description_short', 'order', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'title']
    list_editable = ['order', 'is_active']
    
    def description_short(self, obj):
        return obj.description[:60] + "..." if len(obj.description) > 60 else obj.description
    description_short.short_description = 'Description'
    
    fieldsets = (
        ('Expertise Details', {
            'fields': ('title', 'description', 'icon')
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
