from django import forms
from .models import Credentials

class CredentialForm(forms.ModelForm):
    '''Form for creating and updating credentials.'''
    class Meta:
        model = Credentials
        fields = [
            'title',
            'institution',
            'date_obtained', 
            'icon', 
            'link' 
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the credential'
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'awarding institution'
            }),
            'date_obtained': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Filename of the icon in cv/static/icon'
            }),
            'link': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "URL of the credential's official page"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)