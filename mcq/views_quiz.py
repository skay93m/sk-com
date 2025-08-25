import random
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta
from .models import MCQ, ReviewSchedule, Choice

LABELS = ["A", "B", "C", "D"]

def mcq_index(request):
    """Public MCQ page that shows different content based on authentication status"""
    if request.user.is_authenticated:
        # Redirect authenticated users to the dashboard
        return mcq_dashboard(request)
    else:
        # Show information page for unauthenticated users
        return mcq_info_page(request)

def mcq_info_page(request):
    """Information page about MCQ system for unauthenticated users"""
    # Get some basic public stats
    total_mcqs = MCQ.objects.count()
    
    # Get difficulty distribution
    difficulty_stats = {}
    for difficulty, label in MCQ.DIFFICULTY_CHOICES:
        difficulty_stats[label] = MCQ.objects.filter(difficulty=difficulty).count()
    
    context = {
        'total_mcqs': total_mcqs,
        'difficulty_stats': difficulty_stats,
    }
    
    return render(request, 'mcq_info.html', context)

@login_required
def mcq_dashboard(request):
    """Dashboard page for authenticated users (renamed from mcq_landing)"""
    # Basic stats
    total_mcqs = MCQ.objects.count()
    
    # Due for review count
    due_count = ReviewSchedule.objects.filter(next_review__lte=timezone.now()).count()
    
    # Studied today (simplified - based on schedule updates)
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    studied_today = 0  # This would need session tracking for accurate count
    
    # Next review timing
    next_review = ReviewSchedule.objects.filter(
        next_review__gt=timezone.now()
    ).order_by('next_review').first()
    
    next_review_hours = 0
    if next_review:
        time_diff = next_review.next_review - timezone.now()
        next_review_hours = max(0, int(time_diff.total_seconds() / 3600))
    
    # Difficulty breakdown
    difficulty_stats = {}
    for difficulty, label in MCQ.DIFFICULTY_CHOICES:
        difficulty_stats[label] = MCQ.objects.filter(difficulty=difficulty).count()
    
    context = {
        'total_mcqs': total_mcqs,
        'due_count': due_count,
        'studied_today': studied_today,
        'next_review_hours': next_review_hours,
        'difficulty_stats': difficulty_stats,
    }
    
    return render(request, 'mcq_landing.html', context)

# Keep the old function name for backward compatibility
@login_required
def mcq_landing(request):
    """Landing page with dashboard and navigation options (kept for URL compatibility)"""
    return mcq_dashboard(request)

def get_due_mcq(topics=None):
    """Get the next MCQ that is actually due for review, optionally filtered by topics"""
    qs = ReviewSchedule.objects.filter(next_review__lte=timezone.now()).order_by("next_review")
    
    # Filter by topics if specified
    if topics:
        qs = qs.filter(mcq__topics__in=topics).distinct()
    
    if qs.exists():
        return qs.first().mcq
    return None  # Return None if no questions are due

def get_practice_mcq(topics=None):
    """Get any MCQ for practice mode (ignoring schedule), optionally filtered by topics"""
    qs = MCQ.objects.all()
    
    # Filter by topics if specified
    if topics:
        qs = qs.filter(topics__in=topics).distinct()
    
    return qs.order_by("?").first()

def study(request):
    """Study session with proper spaced repetition - only due questions"""
    # If user is not authenticated, show the description page
    if not request.user.is_authenticated:
        return render(request, "mcq_description.html", {
            'login_url': settings.LOGIN_URL
        })
    
    # Check if there are any MCQs at all
    if not MCQ.objects.exists():
        return render(request, "empty.html")
    
    # Get selected topics from session or request
    selected_topic_ids = request.session.get('study_topics', [])
    if request.method == 'POST' and 'topics' in request.POST:
        selected_topic_ids = [int(id) for id in request.POST.getlist('topics')]
        request.session['study_topics'] = selected_topic_ids
    
    selected_topics = None
    if selected_topic_ids:
        from .models import Topic
        selected_topics = Topic.objects.filter(id__in=selected_topic_ids)
    
    # Get only questions that are actually due (filtered by topics if selected)
    mcq = get_due_mcq(topics=selected_topics)
    if not mcq:
        # No questions due - show the "no questions due" page
        next_review_qs = ReviewSchedule.objects.filter(
            next_review__gt=timezone.now()
        )
        if selected_topics:
            next_review_qs = next_review_qs.filter(mcq__topics__in=selected_topics).distinct()
        
        next_review = next_review_qs.order_by('next_review').first()
        
        next_review_time = None
        next_review_hours = 0
        if next_review:
            next_review_time = next_review.next_review
            time_diff = next_review.next_review - timezone.now()
            next_review_hours = max(0, int(time_diff.total_seconds() / 3600))
        
        context = {
            'next_review_time': next_review_time,
            'next_review_hours': next_review_hours,
            'total_mcqs': MCQ.objects.count(),
            'selected_topics': selected_topics,
        }
        return render(request, "no_questions_due.html", context)
    
    session_key = f"order_mcq_{mcq.id}"
    if request.method == "GET":
        choices = list(mcq.choices.all())
        random.shuffle(choices)
        request.session[session_key] = [c.id for c in choices]
        labeled = [{"label": LABELS[i], "choice": c} for i, c in enumerate(choices)]
        return render(request, "question.html", {"mcq": mcq, "choices_labeled": labeled, "show_feedback": False})
    
    # POST: evaluate
    posted_choice_id = int(request.POST.get("choice_id"))
    order_ids = request.session.get(session_key) or [c.id for c in mcq.choices.all()]
    ordered_choices = [get_object_or_404(Choice, id=i) for i in order_ids]
    labeled = [{"label": LABELS[i], "choice": c} for i, c in enumerate(ordered_choices)]
    
    selected = get_object_or_404(Choice, id=posted_choice_id)
    correct_choice = next(c for c in ordered_choices if c.is_correct)
    
    # Update schedule
    sched = mcq.schedule.first() or ReviewSchedule.objects.create(mcq=mcq)
    sched.schedule_again(correct=(selected.id == correct_choice.id))
    
    # Decide which explanations to show
    feedback = {
        "is_correct": selected.id == correct_choice.id,
        "correct_choice": correct_choice,
        "selected_choice": selected,
        "general_explanation": mcq.explanation_general,
        "selected_explanation": (selected.explanation if not selected.is_correct else ""),
    }
    
    return render(
        request, "question.html",
        {"mcq": mcq, "choices_labeled": labeled, "show_feedback": True, "feedback": feedback}
    )

@login_required 
def practice(request):
    """Practice mode - review any questions without affecting spaced repetition schedule"""
    # Check if there are any MCQs at all
    if not MCQ.objects.exists():
        return render(request, "empty.html")
    
    # Get selected topics from session or request
    selected_topic_ids = request.session.get('practice_topics', [])
    if request.method == 'POST' and 'topics' in request.POST:
        selected_topic_ids = [int(id) for id in request.POST.getlist('topics')]
        request.session['practice_topics'] = selected_topic_ids
    
    selected_topics = None
    if selected_topic_ids:
        from .models import Topic
        selected_topics = Topic.objects.filter(id__in=selected_topic_ids)
    
    mcq = get_practice_mcq(topics=selected_topics)
    if not mcq:
        return render(request, "empty.html")
    
    session_key = f"practice_mcq_{mcq.id}"
    if request.method == "GET":
        choices = list(mcq.choices.all())
        random.shuffle(choices)
        request.session[session_key] = [c.id for c in choices]
        labeled = [{"label": LABELS[i], "choice": c} for i, c in enumerate(choices)]
        
        context = {
            "mcq": mcq, 
            "choices_labeled": labeled, 
            "show_feedback": False,
            "is_practice": True  # Flag to indicate this is practice mode
        }
        return render(request, "question.html", context)
    
    # POST: evaluate (but don't update schedule in practice mode)
    posted_choice_id = int(request.POST.get("choice_id"))
    order_ids = request.session.get(session_key) or [c.id for c in mcq.choices.all()]
    ordered_choices = [get_object_or_404(Choice, id=i) for i in order_ids]
    labeled = [{"label": LABELS[i], "choice": c} for i, c in enumerate(ordered_choices)]
    
    selected = get_object_or_404(Choice, id=posted_choice_id)
    correct_choice = next(c for c in ordered_choices if c.is_correct)
    
    # DON'T update schedule in practice mode
    
    # Decide which explanations to show
    feedback = {
        "is_correct": selected.id == correct_choice.id,
        "correct_choice": correct_choice,
        "selected_choice": selected,
        "general_explanation": mcq.explanation_general,
        "selected_explanation": (selected.explanation if not selected.is_correct else ""),
    }
    
    context = {
        "mcq": mcq, 
        "choices_labeled": labeled, 
        "show_feedback": True, 
        "feedback": feedback,
        "is_practice": True
    }
    return render(request, "question.html", context)

@login_required
def stats(request):
    """Enhanced statistics page with SRS stage breakdown"""
    total_mcqs = MCQ.objects.count()
    
    # Difficulty breakdown
    difficulty_stats = []
    for difficulty, label in MCQ.DIFFICULTY_CHOICES:
        count = MCQ.objects.filter(difficulty=difficulty).count()
        percentage = (count / total_mcqs * 100) if total_mcqs > 0 else 0
        difficulty_stats.append({
            'label': label,
            'count': count,
            'percentage': round(percentage, 1)
        })
    
    # SRS stage breakdown
    srs_stats = []
    for stage, label in ReviewSchedule.SRS_STAGES:
        count = ReviewSchedule.objects.filter(srs_stage=stage).count()
        percentage = (count / total_mcqs * 100) if total_mcqs > 0 else 0
        
        # Get color for this stage
        stage_colors = {
            0: 'secondary', 1: 'danger', 2: 'danger', 3: 'warning', 4: 'warning',
            5: 'info', 6: 'info', 7: 'primary', 8: 'success', 9: 'dark'
        }
        
        srs_stats.append({
            'stage': stage,
            'label': label,
            'count': count,
            'percentage': round(percentage, 1),
            'color': stage_colors.get(stage, 'secondary')
        })
    
    # Review schedule stats
    due_now = ReviewSchedule.objects.filter(next_review__lte=timezone.now()).count()
    
    # Upcoming reviews in next 7 days
    week_from_now = timezone.now() + timedelta(days=7)
    upcoming_week = ReviewSchedule.objects.filter(
        next_review__gt=timezone.now(),
        next_review__lte=week_from_now
    ).count()
    
    # Average SRS stage
    avg_srs_stage = ReviewSchedule.objects.aggregate(
        avg_stage=Avg('srs_stage')
    )['avg_stage'] or 0
    
    # Total reviews completed
    total_reviews = ReviewSchedule.objects.aggregate(
        total=Sum('total_reviews')
    )['total'] or 0
    
    context = {
        'total_mcqs': total_mcqs,
        'difficulty_stats': difficulty_stats,
        'srs_stats': srs_stats,
        'due_now': due_now,
        'upcoming_week': upcoming_week,
        'avg_srs_stage': round(avg_srs_stage, 1),
        'total_reviews': total_reviews,
    }
    
    return render(request, 'mcq_stats.html', context)

@login_required
def topic_selection(request):
    """Topic selection for focused study sessions"""
    from .models import Topic
    from .forms import TopicFilterForm
    
    if request.method == 'POST':
        form = TopicFilterForm(request.POST)
        if form.is_valid():
            selected_topics = form.cleaned_data['topics']
            topic_ids = [topic.id for topic in selected_topics]
            
            # Store in session based on study type
            study_type = request.POST.get('study_type', 'study')
            if study_type == 'practice':
                request.session['practice_topics'] = topic_ids
                return redirect('mcq:practice')
            else:
                request.session['study_topics'] = topic_ids
                return redirect('mcq:study')
    else:
        form = TopicFilterForm()
    
    # Get topic statistics
    topics_stats = []
    for topic in Topic.objects.all():
        due_count = ReviewSchedule.objects.filter(
            mcq__topics=topic,
            next_review__lte=timezone.now()
        ).count()
        total_count = topic.get_mcq_count()
        
        topics_stats.append({
            'topic': topic,
            'total_count': total_count,
            'due_count': due_count,
        })
    
    context = {
        'form': form,
        'topics_stats': topics_stats,
        'total_due': ReviewSchedule.objects.filter(next_review__lte=timezone.now()).count(),
    }
    
    return render(request, 'topic_selection.html', context)

@login_required
def manage_topics(request):
    """Manage topics - create, edit, delete"""
    from .models import Topic
    from .forms import TopicForm
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('mcq:manage_topics')
    else:
        form = TopicForm()
    
    topics = Topic.objects.all().order_by('name')
    
    context = {
        'form': form,
        'topics': topics,
    }
    
    return render(request, 'manage_topics.html', context)