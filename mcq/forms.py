from django import forms
from django.forms import inlineformset_factory
from .models import MCQ, Choice, Topic

# MCQForm
class MCQForm(forms.ModelForm):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select topics/tags for this question"
    )
    
    class Meta:
        model = MCQ
        fields = ["question_text", "difficulty", "explanation_general", "topics"]
        help_texts = {
            "difficulty": "1: Recall - 2: Application - 3: Reasoning",
        }

# Topic creation form
class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ["name", "description", "color"]
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'name': 'Short, descriptive name for the topic',
            'color': 'Color for topic badges in the interface',
        }

# Topic filter form for study sessions
class TopicFilterForm(forms.Form):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select topics to study"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add counts to topic choices
        choices = []
        for topic in Topic.objects.all():
            count = topic.get_mcq_count()
            choices.append((topic.id, f"{topic.name} ({count})"))
        self.fields['topics'].choices = choices

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