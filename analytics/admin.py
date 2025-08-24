"""
Analytics admin interface for viewing and managing analytics data.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import PageView, DailyStats, PopularPage


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'method', 'path', 'status_code', 
        'ip_address', 'response_time_ms', 'is_bot', 'is_mobile'
    ]
    list_filter = [
        'method', 'status_code', 'is_bot', 'is_mobile', 
        'timestamp'
    ]
    search_fields = ['path', 'ip_address', 'user_agent']
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('method', 'path', 'status_code', 'response_time_ms')
        }),
        ('Client Info', {
            'fields': ('ip_address', 'user_agent', 'referer', 'is_bot', 'is_mobile')
        }),
        ('Tracking', {
            'fields': ('timestamp', 'session_key', 'user')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition


@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_views', 'unique_visitors', 'bot_requests',
        'mobile_views', 'avg_response_time', 'top_page_views'
    ]
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False


@admin.register(PopularPage)
class PopularPageAdmin(admin.ModelAdmin):
    list_display = [
        'path', 'title', 'total_views', 'unique_views',
        'avg_response_time', 'last_viewed'
    ]
    search_fields = ['path', 'title']
    readonly_fields = ['first_viewed', 'last_viewed']
    ordering = ['-total_views']
    
    def has_add_permission(self, request):
        return False


# Custom admin views for analytics dashboard
class AnalyticsAdminSite(admin.AdminSite):
    site_header = "Analytics Dashboard"
    site_title = "Analytics"
    index_title = "Website Analytics"
