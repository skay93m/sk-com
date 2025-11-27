from django.contrib import admin
from .models import WorkingIdentity, IdentityFeed


class IdentityFeedInline(admin.TabularInline):
    model = IdentityFeed
    extra = 1
    fields = ['status', 'next_action', 'notes']
    readonly_fields = []
    ordering = ['-date']


@admin.register(WorkingIdentity)
class WorkingIdentityAdmin(admin.ModelAdmin):
    list_display = ['identity', 'description', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [IdentityFeedInline]
    fieldsets = (
        ('Identity', {
            'fields': ('identity', 'description')
        }),
        ('Experiment Plan', {
            'fields': ('experiment_plan',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IdentityFeed)
class IdentityFeedAdmin(admin.ModelAdmin):
    list_display = ['working_identity', 'date', 'status']
    list_filter = ['working_identity', 'date']
    search_fields = ['status', 'next_action', 'notes']
    readonly_fields = ['date']
    ordering = ['-date']