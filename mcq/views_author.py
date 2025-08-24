# mcq/views_author.py (authoring)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import MCQForm, ChoiceFormSet, validate_single_correct
from .models import MCQ, Choice, ReviewSchedule

@login_required
def create_mcq(request):
    if request.method == "POST":
        form = MCQForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            validate_single_correct(formset)
            mcq = form.save()
            formset.instance = mcq
            formset.save()
            # Create initial review schedule
            ReviewSchedule.objects.create(mcq=mcq)
            messages.success(request, "MCQ created successfully!")
            return redirect("mcq:mcq_list")
    else:
        form = MCQForm()
        formset = ChoiceFormSet()
    
    return render(request, "create_mcq.html", {"form": form, "formset": formset})

@login_required
def mcq_list(request):
    """List all MCQs with pagination and basic stats"""
    mcq_queryset = MCQ.objects.all().order_by('-id')
    
    # Add pagination
    paginator = Paginator(mcq_queryset, 10)  # 10 MCQs per page
    page_number = request.GET.get('page')
    mcqs = paginator.get_page(page_number)
    
    # Basic statistics
    total_mcqs = MCQ.objects.count()
    difficulty_stats = {}
    for difficulty, label in MCQ.DIFFICULTY_CHOICES:
        difficulty_stats[label] = MCQ.objects.filter(difficulty=difficulty).count()
    
    context = {
        'mcqs': mcqs,
        'total_mcqs': total_mcqs,
        'difficulty_stats': difficulty_stats,
    }
    
    return render(request, "mcq_list.html", context)

@login_required
def edit_mcq(request, mcq_id):
    """Edit an existing MCQ"""
    mcq = get_object_or_404(MCQ, id=mcq_id)
    
    if request.method == "POST":
        form = MCQForm(request.POST, instance=mcq)
        formset = ChoiceFormSet(request.POST, instance=mcq)
        if form.is_valid() and formset.is_valid():
            validate_single_correct(formset)
            mcq = form.save()
            formset.save()
            messages.success(request, "MCQ updated successfully!")
            return redirect("mcq:mcq_list")
    else:
        form = MCQForm(instance=mcq)
        formset = ChoiceFormSet(instance=mcq)
    
    return render(request, "edit_mcq.html", {
        "form": form, 
        "formset": formset, 
        "mcq": mcq
    })

@login_required
def delete_mcq(request, mcq_id):
    """Delete an MCQ"""
    mcq = get_object_or_404(MCQ, id=mcq_id)
    
    if request.method == "POST":
        mcq.delete()
        messages.success(request, "MCQ deleted successfully!")
        return redirect("mcq:mcq_list")
    
    return render(request, "delete_mcq.html", {"mcq": mcq})