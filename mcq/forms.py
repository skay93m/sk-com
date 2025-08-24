from django import forms
from django.forms import inlineformset_factory
from .models import MCQ, Choice, Topic, QuestionGeneration, GeneratedQuestion, GeneratedChoice

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

# LLM Question Generation Forms
class LLMPromptForm(forms.ModelForm):
    """Form for entering LLM prompts to generate questions"""
    class Meta:
        model = QuestionGeneration
        fields = ['prompt_text', 'topic', 'difficulty']
        widgets = {
            'prompt_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter your prompt for the LLM to generate questions...\n\nExample:\nGenerate 5 multiple choice questions about Python dictionaries.\nEach question should have 4 choices with only one correct answer.\nInclude explanations for both correct and incorrect answers.\nDifficulty level: Intermediate'
            }),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'prompt_text': 'LLM Prompt',
            'topic': 'Topic (Optional)',
            'difficulty': 'Default Difficulty Level',
        }

class LLMResponseForm(forms.ModelForm):
    """Form for pasting LLM response"""
    class Meta:
        model = QuestionGeneration
        fields = ['llm_response']
        widgets = {
            'llm_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Paste the LLM response here...'
            }),
        }
        labels = {
            'llm_response': 'LLM Response',
        }

class GeneratedQuestionReviewForm(forms.ModelForm):
    """Form for reviewing generated questions"""
    class Meta:
        model = GeneratedQuestion
        fields = ['question_text', 'difficulty', 'explanation_general', 'topics', 'status', 'reviewer_notes']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'explanation_general': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'topics': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reviewer_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class GeneratedChoiceForm(forms.ModelForm):
    """Form for editing generated choices"""
    class Meta:
        model = GeneratedChoice
        fields = ['text', 'is_correct', 'explanation']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }