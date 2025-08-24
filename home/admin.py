from django.contrib import admin
from .models import Hero

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
