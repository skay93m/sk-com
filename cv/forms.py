from django import forms
from .models import Credentials
import os
from django.conf import settings
from django.core.files.storage import default_storage
import uuid

def get_existing_icons():
    """Get list of existing icons in the static/icon directory"""
    icon_dir = os.path.join(settings.BASE_DIR, 'cv', 'static', 'icon')
    if os.path.exists(icon_dir):
        icons = []
        for filename in os.listdir(icon_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                icons.append((filename, filename))
        return [('', 'Select an existing icon')] + icons
    return [('', 'No existing icons found')]

class CredentialForm(forms.ModelForm):
    '''Form for creating and updating credentials.'''
    
    # Choice between existing icon or uploading new one
    icon_choice = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'icon-choice'
        }),
        label='Select Existing Icon'
    )
    
    # File upload for new icon
    icon_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'icon-upload'
        }),
        label='Upload New Icon',
        help_text='Upload PNG, JPG, or SVG files. File will be saved to cv/static/icon/'
    )
    
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
            'date_obtained': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'icon': forms.HiddenInput(),  # Hidden field, we'll handle this through the other fields
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': "URL of the credential's official page"
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate existing icon choices
        self.fields['icon_choice'].choices = get_existing_icons()
        
        # Make the hidden icon field not required since we handle it in clean()
        self.fields['icon'].required = False
        
        # If editing an existing credential, set the current icon
        if self.instance and self.instance.icon:
            self.fields['icon_choice'].initial = self.instance.icon
    
    def clean(self):
        cleaned_data = super().clean()
        icon_choice = cleaned_data.get('icon_choice')
        icon_upload = cleaned_data.get('icon_upload')
        
        if not icon_choice and not icon_upload:
            raise forms.ValidationError('Please either select an existing icon or upload a new one.')
        
        if icon_choice and icon_upload:
            raise forms.ValidationError('Please choose either an existing icon OR upload a new one, not both.')
        
        # Validate uploaded file
        if icon_upload:
            # Check file extension
            allowed_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.gif']
            file_extension = os.path.splitext(icon_upload.name)[1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f'Invalid file type. Please upload a PNG, JPG, JPEG, SVG, or GIF file.')
            
            # Check file size (5MB limit)
            if icon_upload.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 5MB.')
        
        # Set the icon field value for validation
        if icon_choice:
            cleaned_data['icon'] = icon_choice
        elif icon_upload:
            # We'll set this in save() method after processing the upload
            cleaned_data['icon'] = 'will_be_set_in_save'
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle icon upload
        icon_upload = self.cleaned_data.get('icon_upload')
        icon_choice = self.cleaned_data.get('icon_choice')
        
        if icon_upload:
            try:
                # Save uploaded file to cv/static/icon/
                icon_dir = os.path.join(settings.BASE_DIR, 'cv', 'static', 'icon')
                os.makedirs(icon_dir, exist_ok=True)
                
                # Generate unique filename to avoid conflicts
                file_extension = os.path.splitext(icon_upload.name)[1]
                base_name = os.path.splitext(icon_upload.name)[0]
                unique_filename = f"{base_name}_{uuid.uuid4().hex[:8]}{file_extension}"
                
                file_path = os.path.join(icon_dir, unique_filename)
                
                # Save the file
                with open(file_path, 'wb+') as destination:
                    for chunk in icon_upload.chunks():
                        destination.write(chunk)
                
                instance.icon = unique_filename
            except Exception as e:
                raise forms.ValidationError(f'Error saving icon file: {str(e)}')
        elif icon_choice:
            instance.icon = icon_choice
        
        if commit:
            try:
                instance.save()
            except Exception as e:
                raise forms.ValidationError(f'Error saving credential: {str(e)}')
        
        return instance