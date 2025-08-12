# forms.py

from django import forms
from home.models import Hero

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['title', 'tagline']
    
    widgets = {
            'tagline': forms.Textarea(attrs={'rows': 3}),
        }

