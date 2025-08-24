from django.contrib import admin
from .models import Credentials

@admin.register(Credentials)
class CredentialsAdmin(admin.ModelAdmin):
    """Admin interface for Credentials model"""
    
    list_display = ['title', 'institution', 'date_obtained', 'icon']
    list_filter = ['institution', 'date_obtained']
    search_fields = ['title', 'institution']
    readonly_fields = []
    date_hierarchy = 'date_obtained'
    
    fieldsets = (
        ('Credential Information', {
            'fields': ('title', 'institution', 'date_obtained')
        }),
        ('Display Settings', {
            'fields': ('icon', 'link'),
            'description': 'Icon filename should be placed in cv/static/icon/ directory'
        }),
    )
