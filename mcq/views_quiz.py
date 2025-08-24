import random
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import MCQ, ReviewSchedule, Choice

LABELS = ["A", "B", "C", "D"]

def get_due_mcq():
    # simplest: earliest due item; ensure each MCQ has a schedule
    qs = ReviewSchedule.objects.filter(next_review__lte=timezone.now()).order_by("next_review")
    if qs.exists():
        return qs.first().mcq
    # if none due, offer nearest upcoming as practice
    upcoming = ReviewSchedule.objects.order_by("next_review").first()
    return upcoming.mcq if upcoming else MCQ.objects.order_by("?").first()

def quiz(request):
    # If user is not authenticated, show the description page
    if not request.user.is_authenticated:
        return render(request, "mcq_description.html", {
            'login_url': settings.LOGIN_URL
        })
    
    mcq = get_due_mcq()
    if not mcq:
        return render(request, "empty.html")
    
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