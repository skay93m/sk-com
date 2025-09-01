from django.db import models
from django.urls import reverse

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('now', 'Current'),
        ('backburner', 'Backburner'),
        ('someday', 'Someday'),
    ]

    # Basic Project Info
    title = models.CharField(max_length=200, verbose_name="Project Name")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='someday')
    
    # Project Overview
    purpose = models.TextField(blank=True, help_text='Purpose/Goal of the project')
    success_criteria = models.TextField(blank=True, help_text='Define what success looks like')
    
    # Key Considerations
    stakeholders = models.TextField(blank=True, help_text='Who is involved or affected?')
    constraints = models.TextField(blank=True, help_text='Limitations and boundaries')
    risks = models.TextField(blank=True, help_text='Potential risks and mitigation strategies')
    dependencies = models.TextField(blank=True, help_text='What this project depends on')
    
    # Resources
    tools_needed = models.TextField(blank=True, help_text='Tools and software required')
    people_needed = models.TextField(blank=True, help_text='Team members and roles')
    budget = models.TextField(blank=True, help_text='Budget requirements')
    knowledge_training = models.TextField(blank=True, help_text='Skills and training needed')
    
    # Tracking & Review
    progress_checkpoints = models.TextField(blank=True, help_text='How will progress be tracked?')
    adjustments_flexibility = models.TextField(blank=True, help_text='Areas where adjustments can be made')
    final_review_learnings = models.TextField(blank=True, help_text='Post-project review and learnings')
    
    # Legacy field for backward compatibility
    description = models.TextField(blank=True, help_text='General project description')
    plan = models.TextField(blank=True, help_text='Project plan notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})

class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200, verbose_name="Milestone")
    description = models.TextField(help_text='Description of what this milestone achieves')
    target_date = models.DateField(null=True, blank=True)
    owner = models.CharField(max_length=100, blank=True, help_text='Who is responsible for this milestone')
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Order of milestone in the project')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'target_date']

    def __str__(self):
        return f'{self.project.title} - {self.title}'

class ProjectTask(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Task")
    description = models.TextField(blank=True, help_text='Detailed task description')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    notes = models.TextField(blank=True, help_text='Additional notes and updates')
    order = models.PositiveIntegerField(default=0, help_text='Order of task within milestone/project')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'deadline']

    def __str__(self):
        return f'{self.project.title} - {self.title}'

class ProjectActivity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    log = models.TextField(help_text='Activity log, comments, or ideas')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Project Activities'

    def __str__(self):
        return f'Activity for {self.project.title} at {self.created_at.strftime("%Y-%m-%d %H:%M")}'
