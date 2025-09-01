# forms.py

from django import forms
from home.models import Hero, Expertise

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['header', 'tagline']
    
    widgets = {
            'tagline': forms.Textarea(attrs={'rows': 3}),
        }


class ExpertiseForm(forms.ModelForm):
    class Meta:
        model = Expertise
        fields = ['title', 'description', 'icon', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'icon': forms.TextInput(attrs={'placeholder': 'e.g., 🏥'}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }

