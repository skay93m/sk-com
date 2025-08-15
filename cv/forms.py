from django import forms

class CredentialForm(forms.Form):
    name = forms.CharField(max_length=100)
    details = forms.CharField(widget=forms.Textarea)
