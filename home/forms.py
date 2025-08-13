# forms.py

from django import forms
from home.models import Hero

class HeroForm(forms.ModelForm):
    class Meta:
        model = Hero
        fields = ['header', 'tagline']
    
    widgets = {
            'tagline': forms.Textarea(attrs={'rows': 3}),
        }

