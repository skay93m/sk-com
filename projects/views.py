from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .models import Project, ProjectActivity, ProjectMilestone, ProjectTask
from .forms import ProjectForm, ProjectActivityForm, ProjectMilestoneForm, ProjectTaskForm
from django.conf import settings
import markdown
import os

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    activities = project.activities.all()[:10]  # Latest 10 activities
    milestones = project.milestones.all()
    tasks = project.tasks.all()
    
    # Forms for adding new items
    activity_form = ProjectActivityForm()
    milestone_form = ProjectMilestoneForm()
    task_form = ProjectTaskForm(project=project)

    if request.method == 'POST':
        if 'add_activity' in request.POST:
            activity_form = ProjectActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.project = project
                activity.save()
                messages.success(request, 'Activity added successfully!')
                return redirect('projects:project_detail', pk=project.pk)
        
        elif 'add_milestone' in request.POST:
            milestone_form = ProjectMilestoneForm(request.POST)
            if milestone_form.is_valid():
                milestone = milestone_form.save(commit=False)
                milestone.project = project
                milestone.save()
                messages.success(request, 'Milestone added successfully!')
                return redirect('projects:project_detail', pk=project.pk)
        
        elif 'add_task' in request.POST:
            task_form = ProjectTaskForm(project, request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.save()
                messages.success(request, 'Task added successfully!')
                return redirect('projects:project_detail', pk=project.pk)

    # Convert markdown fields to HTML for display
    project.purpose_html = markdown.markdown(project.purpose) if project.purpose else ''
    project.plan_html = markdown.markdown(project.plan) if project.plan else ''

    return render(request, 'project_detail.html', {
        'project': project,
        'activities': activities,
        'milestones': milestones,
        'tasks': tasks,
        'activity_form': activity_form,
        'milestone_form': milestone_form,
        'task_form': task_form,
    })

def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.title}" created successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})

def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.title}" updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_edit.html', {'form': form, 'project': project})

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" deleted successfully!')
        return redirect('projects:project_list')
    return render(request, 'project_delete.html', {'project': project})

# Milestone views
def milestone_edit(request, pk, milestone_pk):
    project = get_object_or_404(Project, pk=pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
    
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, f'Milestone "{milestone.title}" updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectMilestoneForm(instance=milestone)
    
    return render(request, 'milestone_edit.html', {
        'form': form, 
        'project': project, 
        'milestone': milestone
    })

def milestone_delete(request, pk, milestone_pk):
    project = get_object_or_404(Project, pk=pk)
    milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
    
    if request.method == 'POST':
        milestone_title = milestone.title
        milestone.delete()
        messages.success(request, f'Milestone "{milestone_title}" deleted successfully!')
        return redirect('projects:project_detail', pk=project.pk)
    
    return render(request, 'milestone_delete.html', {
        'project': project, 
        'milestone': milestone
    })

def milestone_toggle_complete(request, pk, milestone_pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        milestone = get_object_or_404(ProjectMilestone, pk=milestone_pk, project=project)
        milestone.completed = not milestone.completed
        if milestone.completed:
            from django.utils import timezone
            milestone.completed_date = timezone.now().date()
        else:
            milestone.completed_date = None
        milestone.save()
        
        return JsonResponse({
            'success': True, 
            'completed': milestone.completed,
            'completed_date': milestone.completed_date.isoformat() if milestone.completed_date else None
        })
    
    return JsonResponse({'success': False})

# Task views
def task_edit(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
    
    if request.method == 'POST':
        form = ProjectTaskForm(project, request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectTaskForm(project, instance=task)
    
    return render(request, 'task_edit.html', {
        'form': form, 
        'project': project, 
        'task': task
    })

def task_delete(request, pk, task_pk):
    project = get_object_or_404(Project, pk=pk)
    task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
    
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('projects:project_detail', pk=project.pk)
    
    return render(request, 'task_delete.html', {
        'project': project, 
        'task': task
    })

def task_update_status(request, pk, task_pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        task = get_object_or_404(ProjectTask, pk=task_pk, project=project)
        new_status = request.POST.get('status')
        
        if new_status in dict(ProjectTask.STATUS_CHOICES):
            task.status = new_status
            task.save()
            
            return JsonResponse({
                'success': True, 
                'status': task.status,
                'status_display': task.get_status_display()
            })
    
    return JsonResponse({'success': False})

def project_template_download(request):
    """Generate and download the project plan template as markdown."""
    
    template_content = """# 🧠 Project Planning Template

## 1. Project Overview
- **Project Name**: [Enter your project name here]
- **Purpose / Goal**: [What are you trying to achieve?]
- **Success Criteria**: [How will you know when you've succeeded?]

---

## 2. Key Considerations
- **Stakeholders**: [Who is involved or affected by this project?]
- **Constraints**: [What limitations or boundaries do you have?]
- **Risks**: [What could go wrong and how will you mitigate it?]
- **Dependencies**: [What does this project depend on?]

---

## 3. Milestones
Break the project into major phases or checkpoints.

| Milestone | Description | Target Date | Owner |
|-----------|-------------|-------------|-------|
| [Milestone 1] | [What will be achieved] | [YYYY-MM-DD] | [Person responsible] |
| [Milestone 2] | [What will be achieved] | [YYYY-MM-DD] | [Person responsible] |
| [Add more as needed] | | | |

---

## 4. Action Plan
Detailed tasks to move the project forward.

| Task | Priority | Deadline | Status | Notes |
|------|----------|----------|--------|-------|
| [Task 1] | High/Med/Low | [YYYY-MM-DD] | Not Started/In Progress/Done | [Additional notes] |
| [Task 2] | High/Med/Low | [YYYY-MM-DD] | Not Started/In Progress/Done | [Additional notes] |
| [Add more as needed] | | | | |

---

## 5. Resources Needed
- **Tools**: [Software, equipment, systems needed]
- **People**: [Team members, roles, external help]
- **Budget**: [Financial requirements]
- **Knowledge / Training**: [Skills or training required]

---

## 6. Tracking & Review
- **Progress Checkpoints**: [How often will you review progress? Weekly? Monthly?]
- **Adjustments / Flexibility**: [What areas can be adjusted if needed?]
- **Final Review & Learnings**: [How will you capture lessons learned?]

---

> 💡 **Tip**: Revisit this plan weekly to stay aligned and adapt as needed.

---

*Generated from SK Project Management System*
*Template created on: {date}*
"""
    
    from datetime import datetime
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = template_content.format(date=formatted_date)
    
    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = 'attachment; filename="project_plan_template.md"'
    return response

def project_create_from_template(request):
    """Create a new project with pre-filled template structure."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            
            # Add default milestones based on template
            default_milestones = [
                {'title': 'Project Planning', 'description': 'Complete initial project planning and setup', 'order': 1},
                {'title': 'Development Phase', 'description': 'Core development and implementation work', 'order': 2},
                {'title': 'Testing & Review', 'description': 'Testing, review, and refinement', 'order': 3},
                {'title': 'Project Completion', 'description': 'Final delivery and project closure', 'order': 4},
            ]
            
            for milestone_data in default_milestones:
                ProjectMilestone.objects.create(
                    project=project,
                    title=milestone_data['title'],
                    description=milestone_data['description'],
                    order=milestone_data['order']
                )
            
            # Add some default tasks
            default_tasks = [
                {'title': 'Define project scope', 'priority': 'high', 'order': 1},
                {'title': 'Identify key stakeholders', 'priority': 'high', 'order': 2},
                {'title': 'Set up project resources', 'priority': 'medium', 'order': 3},
                {'title': 'Create project timeline', 'priority': 'medium', 'order': 4},
            ]
            
            first_milestone = project.milestones.first()
            for task_data in default_tasks:
                ProjectTask.objects.create(
                    project=project,
                    milestone=first_milestone,
                    title=task_data['title'],
                    priority=task_data['priority'],
                    order=task_data['order']
                )
            
            messages.success(request, f'Project "{project.title}" created from template with default milestones and tasks!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        # Pre-fill form with template guidance
        initial_data = {
            'progress_checkpoints': 'Weekly progress reviews\nMonthly milestone assessments\nQuarterly strategic reviews',
            'adjustments_flexibility': 'Timeline can be adjusted by ±20%\nScope changes require stakeholder approval\nResource allocation can be optimized as needed',
            'final_review_learnings': 'Conduct post-project retrospective\nDocument lessons learned\nUpdate project templates and processes\nShare insights with team',
        }
        form = ProjectForm(initial=initial_data)
    
    return render(request, 'project_create_from_template.html', {'form': form})
