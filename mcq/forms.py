from django import forms
from django.forms import inlineformset_factory
from .models import MCQ, Choice

# MCQForm
class MCQForm(forms.ModelForm):
    class Meta:
        model = MCQ
        fields = ["question_text", "difficulty", "explanation_general"]
        help_texts = {
            "difficulty": "1: Recall - 2: Application - 3: Reasoning",
        }

# ChoiceFormSet
ChoiceFormSet = inlineformset_factory(
    MCQ, Choice,
    fields=["text", "is_correct", "explanation"],
    extra=4, min_num=2, validate_min=True, can_delete=True
)

def validate_single_correct(formset):
    correct_count = sum(1 for f in formset if not f.cleaned_data.get("DELETE") and f.cleaned_data.get("is_correct"))
    if correct_count != 1:
        raise forms.ValidationError("Exactly one choice must be marked correct.")