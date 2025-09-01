from django import forms
from .models import Project, ProjectActivity, ProjectMilestone, ProjectTask

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'category', 'purpose', 'success_criteria',
            'stakeholders', 'constraints', 'risks', 'dependencies',
            'tools_needed', 'people_needed', 'budget', 'knowledge_training',
            'progress_checkpoints', 'adjustments_flexibility', 'final_review_learnings',
            'description', 'plan'
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
            'success_criteria': forms.Textarea(attrs={'rows': 3}),
            'stakeholders': forms.Textarea(attrs={'rows': 2}),
            'constraints': forms.Textarea(attrs={'rows': 2}),
            'risks': forms.Textarea(attrs={'rows': 3}),
            'dependencies': forms.Textarea(attrs={'rows': 2}),
            'tools_needed': forms.Textarea(attrs={'rows': 2}),
            'people_needed': forms.Textarea(attrs={'rows': 2}),
            'budget': forms.Textarea(attrs={'rows': 2}),
            'knowledge_training': forms.Textarea(attrs={'rows': 2}),
            'progress_checkpoints': forms.Textarea(attrs={'rows': 2}),
            'adjustments_flexibility': forms.Textarea(attrs={'rows': 2}),
            'final_review_learnings': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'plan': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})

class ProjectMilestoneForm(forms.ModelForm):
    class Meta:
        model = ProjectMilestone
        fields = ['title', 'description', 'target_date', 'owner', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})

class ProjectTaskForm(forms.ModelForm):
    class Meta:
        model = ProjectTask
        fields = ['title', 'description', 'milestone', 'priority', 'deadline', 'status', 'notes', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            self.fields['milestone'].queryset = ProjectMilestone.objects.filter(project=project)
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'form-control'})

class ProjectActivityForm(forms.ModelForm):
    class Meta:
        model = ProjectActivity
        fields = ['log']
        widgets = {
            'log': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Log an activity, comment, or idea...', 'class': 'form-control'}),
        }
        labels = {
            'log': ''
        }