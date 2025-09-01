from django import template

register = template.Library()

@register.filter
def completed_milestones(project):
    """Return the count of completed milestones for a project."""
    return project.projectmilestone_set.filter(completed=True).count()

@register.filter
def total_milestones(project):
    """Return the total count of milestones for a project."""
    return project.projectmilestone_set.count()

@register.filter
def progress_percentage(project):
    """Calculate the progress percentage of a project based on completed milestones."""
    total = project.projectmilestone_set.count()
    if total == 0:
        return 0
    completed = project.projectmilestone_set.filter(completed=True).count()
    return int((completed / total) * 100)
