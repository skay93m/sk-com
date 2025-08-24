"""
Views for LLM-powered question generation workflow
"""

import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.db import transaction

from .models import (
    QuestionGeneration, GeneratedQuestion, GeneratedChoice, 
    MCQ, Choice, Topic, ReviewSchedule
)
from .forms import LLMPromptForm, LLMResponseForm, GeneratedQuestionReviewForm


def llm_generation_home(request):
    """Landing page for LLM question generation"""
    recent_sessions = QuestionGeneration.objects.all()[:10]
    
    context = {
        'recent_sessions': recent_sessions,
        'pending_review_count': GeneratedQuestion.objects.filter(status='pending').count(),
    }
    return render(request, 'mcq/llm_generation_home.html', context)


def create_llm_prompt(request):
    """Step 1: Create prompt for LLM"""
    if request.method == 'POST':
        form = LLMPromptForm(request.POST)
        if form.is_valid():
            generation = form.save()
            return redirect('mcq:llm_paste_response', generation_id=generation.id)
    else:
        form = LLMPromptForm()
    
    return render(request, 'mcq/llm_prompt.html', {'form': form})


def paste_llm_response(request, generation_id):
    """Step 2: Paste LLM response and parse questions"""
    generation = get_object_or_404(QuestionGeneration, id=generation_id)
    
    if request.method == 'POST':
        form = LLMResponseForm(request.POST, instance=generation)
        if form.is_valid():
            generation = form.save()
            generation.status = 'reviewing'
            generation.save()
            
            # Parse the LLM response and create GeneratedQuestion objects
            try:
                parsed_count = parse_llm_response(generation)
                messages.success(
                    request, 
                    f"Successfully parsed {parsed_count} questions from LLM response. "
                    f"Please review each question before adding to the database."
                )
                return redirect('mcq:review_generated_questions', generation_id=generation.id)
            except Exception as e:
                messages.error(request, f"Error parsing LLM response: {str(e)}")
                return redirect('mcq:llm_paste_response', generation_id=generation.id)
    else:
        form = LLMResponseForm(instance=generation)
    
    context = {
        'form': form,
        'generation': generation,
    }
    return render(request, 'mcq/llm_response.html', context)


def review_generated_questions(request, generation_id):
    """Step 3: Review and approve/reject generated questions"""
    generation = get_object_or_404(QuestionGeneration, id=generation_id)
    questions = generation.questions.all().order_by('created_at')
    
    context = {
        'generation': generation,
        'questions': questions,
    }
    return render(request, 'mcq/review_generated_questions.html', context)


def review_single_question(request, question_id):
    """Review a single generated question"""
    question = get_object_or_404(GeneratedQuestion, id=question_id)
    
    if request.method == 'POST':
        form = GeneratedQuestionReviewForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            question.reviewed_at = timezone.now()
            question.save()
            
            # If approved, convert to MCQ
            if question.status == 'approved':
                try:
                    create_mcq_from_generated(question)
                    messages.success(request, f"Question approved and added to database!")
                except Exception as e:
                    messages.error(request, f"Error creating MCQ: {str(e)}")
            
            return redirect('mcq:review_generated_questions', generation_id=question.generation_session.id)
    else:
        form = GeneratedQuestionReviewForm(instance=question)
    
    context = {
        'form': form,
        'question': question,
        'choices': question.choices.all(),
    }
    return render(request, 'mcq/review_single_question.html', context)


def finalize_generation_session(request, generation_id):
    """Finalize the generation session"""
    generation = get_object_or_404(QuestionGeneration, id=generation_id)
    
    approved_count = generation.questions.filter(status='approved').count()
    rejected_count = generation.questions.filter(status='rejected').count()
    pending_count = generation.questions.filter(status='pending').count()
    
    if pending_count > 0:
        messages.warning(request, f"There are still {pending_count} questions pending review.")
        return redirect('mcq:review_generated_questions', generation_id=generation_id)
    
    generation.status = 'completed'
    generation.completed_at = timezone.now()
    generation.save()
    
    messages.success(
        request, 
        f"Generation session completed! {approved_count} questions approved, {rejected_count} rejected."
    )
    return redirect('mcq:llm_generation_home')


def parse_llm_response(generation):
    """
    Parse LLM response and create GeneratedQuestion and GeneratedChoice objects
    This is a flexible parser that handles various LLM response formats
    """
    response_text = generation.llm_response
    
    # Try to detect JSON format first
    if response_text.strip().startswith('{') or response_text.strip().startswith('['):
        try:
            return parse_json_response(generation, response_text)
        except:
            pass
    
    # Fall back to text parsing
    return parse_text_response(generation, response_text)


def parse_json_response(generation, response_text):
    """Parse JSON formatted LLM response"""
    data = json.loads(response_text)
    
    # Handle different JSON structures
    if isinstance(data, list):
        questions_data = data
    elif isinstance(data, dict):
        if 'questions' in data:
            questions_data = data['questions']
        elif 'mcqs' in data:
            questions_data = data['mcqs']
        else:
            # Assume the dict itself is a single question
            questions_data = [data]
    
    count = 0
    for q_data in questions_data:
        question = GeneratedQuestion.objects.create(
            generation_session=generation,
            question_text=q_data.get('question', q_data.get('question_text', '')),
            difficulty=q_data.get('difficulty', generation.difficulty),
            explanation_general=q_data.get('explanation', q_data.get('explanation_general', ''))
        )
        
        # Add topics if specified
        if generation.topic:
            question.topics.add(generation.topic)
        
        # Create choices
        choices_data = q_data.get('choices', q_data.get('options', []))
        for choice_data in choices_data:
            if isinstance(choice_data, str):
                # Simple string format, guess if correct
                GeneratedChoice.objects.create(
                    generated_question=question,
                    text=choice_data,
                    is_correct=False  # Will need manual review
                )
            else:
                GeneratedChoice.objects.create(
                    generated_question=question,
                    text=choice_data.get('text', choice_data.get('option', '')),
                    is_correct=choice_data.get('is_correct', choice_data.get('correct', False)),
                    explanation=choice_data.get('explanation', '')
                )
        count += 1
    
    return count


def parse_text_response(generation, response_text):
    """Parse text formatted LLM response using regex patterns"""
    # Split by question patterns
    question_pattern = r'(?:Question\s*\d+|Q\d+|\d+\.)\s*[:.]?\s*(.+?)(?=(?:Question\s*\d+|Q\d+|\d+\.|$))'
    questions = re.findall(question_pattern, response_text, re.DOTALL | re.IGNORECASE)
    
    count = 0
    for q_text in questions:
        if not q_text.strip():
            continue
            
        # Extract question text and choices
        lines = [line.strip() for line in q_text.split('\n') if line.strip()]
        
        if not lines:
            continue
        
        # First non-empty line is usually the question
        question_text = lines[0]
        
        # Remove common prefixes
        question_text = re.sub(r'^(?:Question\s*\d*:?\s*|Q\d*:?\s*|\d+\.?\s*)', '', question_text, flags=re.IGNORECASE)
        
        question = GeneratedQuestion.objects.create(
            generation_session=generation,
            question_text=question_text,
            difficulty=generation.difficulty,
        )
        
        # Add default topic if specified
        if generation.topic:
            question.topics.add(generation.topic)
        
        # Extract choices
        choice_pattern = r'^[A-Da-d][.)]\s*(.+)$'
        correct_pattern = r'(?:correct|answer)[:\s]*([A-Da-d])'
        
        correct_letter = None
        # Look for answer indication
        for line in lines:
            match = re.search(correct_pattern, line, re.IGNORECASE)
            if match:
                correct_letter = match.group(1).upper()
                break
        
        choice_letter = 'A'
        for line in lines[1:]:  # Skip question text
            match = re.match(choice_pattern, line)
            if match:
                choice_text = match.group(1)
                is_correct = (choice_letter == correct_letter)
                
                GeneratedChoice.objects.create(
                    generated_question=question,
                    text=choice_text,
                    is_correct=is_correct
                )
                choice_letter = chr(ord(choice_letter) + 1)
        
        count += 1
    
    return count


def create_mcq_from_generated(generated_question):
    """Convert a GeneratedQuestion to an MCQ in the main database"""
    with transaction.atomic():
        # Create the main MCQ
        mcq = MCQ.objects.create(
            question_text=generated_question.question_text,
            difficulty=generated_question.difficulty,
            explanation_general=generated_question.explanation_general,
        )
        
        # Add topics
        mcq.topics.set(generated_question.topics.all())
        
        # Create choices
        for generated_choice in generated_question.choices.all():
            Choice.objects.create(
                mcq=mcq,
                text=generated_choice.text,
                is_correct=generated_choice.is_correct,
                explanation=generated_choice.explanation,
            )
        
        # Create review schedule
        ReviewSchedule.objects.create(mcq=mcq)
        
        # Link back to generated question
        generated_question.final_mcq = mcq
        generated_question.save()
        
        return mcq


def llm_generation_manual(request):
    """Display manual page for LLM generation workflow"""
    return render(request, 'mcq/llm_generation_manual.html')
