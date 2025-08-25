from django.contrib import admin
from .models import Project, ProjectMilestone, ProjectTask, ProjectActivity

class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0
    fields = ['title', 'target_date', 'owner', 'completed', 'order']
    ordering = ['order']

class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0
    fields = ['title', 'priority', 'deadline', 'status', 'milestone']
    ordering = ['order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model"""
    
    list_display = ['title', 'category', 'purpose_short', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'purpose', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [ProjectMilestoneInline, ProjectTaskInline]
    
    def purpose_short(self, obj):
        return obj.purpose[:80] + "..." if len(obj.purpose) > 80 else obj.purpose
    purpose_short.short_description = 'Purpose'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category')
        }),
        ('Project Overview', {
            'fields': ('purpose', 'success_criteria'),
            'classes': ('collapse',)
        }),
        ('Key Considerations', {
            'fields': ('stakeholders', 'constraints', 'risks', 'dependencies'),
            'classes': ('collapse',)
        }),
        ('Resources', {
            'fields': ('tools_needed', 'people_needed', 'budget', 'knowledge_training'),
            'classes': ('collapse',)
        }),
        ('Tracking & Review', {
            'fields': ('progress_checkpoints', 'adjustments_flexibility', 'final_review_learnings'),
            'classes': ('collapse',)
        }),
        ('Legacy Fields', {
            'fields': ('description', 'plan'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'target_date', 'owner', 'completed', 'order']
    list_filter = ['completed', 'project', 'target_date']
    search_fields = ['title', 'description', 'project__title']
    list_editable = ['completed', 'order']
    date_hierarchy = 'target_date'
    
    fieldsets = (
        ('Milestone Information', {
            'fields': ('project', 'title', 'description', 'order')
        }),
        ('Timeline', {
            'fields': ('target_date', 'completed', 'completed_date', 'owner')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'milestone', 'priority', 'deadline', 'status', 'order']
    list_filter = ['priority', 'status', 'project', 'milestone']
    search_fields = ['title', 'description', 'project__title']
    list_editable = ['priority', 'status', 'order']
    date_hierarchy = 'deadline'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('project', 'milestone', 'title', 'description', 'order')
        }),
        ('Planning', {
            'fields': ('priority', 'deadline', 'status')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ['project', 'milestone', 'task', 'log_short', 'created_at']
    list_filter = ['project', 'milestone', 'created_at']
    search_fields = ['log', 'project__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def log_short(self, obj):
        return obj.log[:100] + "..." if len(obj.log) > 100 else obj.log
    log_short.short_description = 'Activity Log'
